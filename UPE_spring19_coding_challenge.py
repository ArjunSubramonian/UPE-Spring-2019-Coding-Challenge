import requests

url = 'http://ec2-34-212-54-152.us-west-2.compute.amazonaws.com' # server url
uid = '205105147' # your uid
resp = requests.post(url + '/session', data = {'uid': uid}) # start new session
body = resp.json()
access_token = body['token'] # retrieve access token from response body

# pretty print 2D array
def pretty_print(matrix):
    s = [[str(e) for e in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))

def solve_maze(xcol, ycol, width, height, maze):
    global url
    global access_token

    # make current position in maze as visited
    maze[xcol][ycol] = 'x'
    solved = False

    # debugging print statements
    print('(' + str(xcol) + ', ' + str(ycol) + ')')
    pretty_print(maze)
    print()
    print()

    # dir: 'up'
    # check that moving in dir keeps you within maze and that you're not moving to position you've already visited/position with wall
    if ycol - 1 >= 0 and maze[xcol][ycol - 1] != 'x':
        resp = requests.post(url + '/game?token=' + access_token, data = {'action' : 'up'}) # move in dir and get maze information
        result = resp.json()["result"]
        # if successful move, solve maze from new position
        if result == 0:
            solved = solve_maze(xcol, ycol - 1, width, height, maze)
            # important to backtrack if don't find solution!
            if not solved:
                requests.post(url + '/game?token=' + access_token, data = {'action' : 'down'})
        elif result == 1:
            solved = True
        # mark any wall encountered
        elif result == -1:
            maze[xcol][ycol - 1] = 'x'

    # dir: 'down'
    # check that moving in dir keeps you within maze and that you're not moving to position you've already visited/position with wall
    if ycol + 1 < height and not solved and maze[xcol][ycol + 1] != 'x':
        resp = requests.post(url + '/game?token=' + access_token, data = {'action' : 'down'}) # move in dir and get maze information
        result = resp.json()["result"]
        # if successful move, solve maze from new position
        if result == 0:
            solved = solve_maze(xcol, ycol + 1, width, height, maze)
            # important to backtrack if don't find solution!
            if not solved:
                requests.post(url + '/game?token=' + access_token, data = {'action' : 'up'})
        elif result == 1:
            solved = True
        # mark any wall encountered
        elif result == -1:
            maze[xcol][ycol + 1] = 'x'
            
    # dir: 'left'
    # check that moving in dir keeps you within maze and that you're not moving to position you've already visited/position with wall
    if xcol - 1 >= 0 and not solved and maze[xcol - 1][ycol] != 'x':
        resp = requests.post(url + '/game?token=' + access_token, data = {'action' : 'left'}) # move in dir and get maze information
        result = resp.json()["result"]
        # if successful move, solve maze from new position
        if result == 0:
            solved = solve_maze(xcol - 1, ycol, width, height, maze)
            # important to backtrack if don't find solution!
            if not solved:
                requests.post(url + '/game?token=' + access_token, data = {'action' : 'right'})
        elif result == 1:
            solved = True
        # mark any wall encountered
        elif result == -1:
            maze[xcol - 1][ycol] = 'x'
          
    # dir: 'right' 
    # check that moving in dir keeps you within maze and that you're not moving to position you've already visited/position with wall
    if xcol + 1 < width and not solved and maze[xcol + 1][ycol] != 'x':
        resp = requests.post(url + '/game?token=' + access_token, data = {'action' : 'right'}) # move in dir and get maze information
        result = resp.json()["result"]
        # if successful move, solve maze from new position
        if result == 0:
            solved = solve_maze(xcol + 1, ycol, width, height, maze)
            # important to backtrack if don't find solution!
            if not solved:
                requests.post(url + '/game?token=' + access_token, data = {'action' : 'left'})
        elif result == 1:
            solved = True
        # mark any wall encountered
        elif result == -1:
            maze[xcol + 1][ycol] = 'x'

    return solved

# loop through levels
level = 1
while True:
    resp = requests.get(url + '/game?token=' + access_token) # get maze information
    body = resp.json()

    # break out of loop is status is “GAME_OVER”, “NONE”, or “FINISHED”
    if body['status'] != 'PLAYING':
        print(body['status'])
        break

    # retrieve information about the maze from response body
    width, height = body['size']
    # initialize empty maze
    maze = []
    for i in range(width):
        maze.append([])
        for j in range(height):
            maze[i].append(0)
    # get current location
    xcol, ycol = body['cur_loc']

    # print solution status
    print('Solved ' + str(level) + ': ' + str(solve_maze(xcol, ycol, width, height, maze)))
    level += 1
