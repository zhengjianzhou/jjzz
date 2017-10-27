import random
import numpy as np

BOARD_SIZE = 11
BOARD_SIZEm1 = BOARD_SIZE-1
BLOCKER = 9


def random_step(in_state, player):
    while 0 in in_state:
        x,y = random.randint(0,BOARD_SIZEm1),random.randint(0,BOARD_SIZEm1)
        if in_state[x,y] == 0:
            in_state[x,y] = player
            return in_state, x, y
    return in_state, -1, -1

def slicer(in_state):
    res = [BLOCKER]
    # mode: 0,1,2,3 => horizontal, vertical, leftup/rightdown, leftdown/rightup
    for i in in_state:
        res.extend(i)
        res.append(BLOCKER)
    for i in in_state.transpose():
        res.extend(i)
        res.append(BLOCKER)
        
    for i in range(BOARD_SIZE):
        res.extend([in_state[i-x,x] for x in range(i+1)])
        res.append(BLOCKER)
    for i in range(BOARD_SIZEm1)[::-1]:
        res.extend([in_state[BOARD_SIZEm1-(i-x),BOARD_SIZEm1-x] for x in range(i+1)[::-1]])
        res.append(BLOCKER)

    for i in range(BOARD_SIZE):
        res.extend([in_state[i-x,BOARD_SIZEm1-x] for x in range(i+1)[::-1]])
        res.append(BLOCKER)
    for i in range(BOARD_SIZEm1)[::-1]:
        res.extend([in_state[BOARD_SIZEm1-(i-x),x] for x in range(i+1)])
        res.append(BLOCKER)
    return res

def push(arr, step=1, filler=0):
    if abs(step) > len(arr):
        return [filler]*(len(arr))
    if step>0:
        return [filler]*abs(step) + arr[:-step]
    else:
        return arr[-step:] + [filler]*(-step)

def check_winner(in_state):
    MAP = {0:0, 1:1, 2:10, BLOCKER:-9999}
    board_state = [MAP[i] for i in slicer(in_state)]
    states = np.array(board_state)
    for i in range(1,5):
        state_i = np.array(push(board_state, i))
        states = states + state_i
    if 5 in states:
        return True, 'Player 1 wins.'
    if 50 in states:
        return True, 'Player 2 wins.'
    return False, 'Nothing.'

historical_states = []
historical_moves = []

state = np.array([[0]*BOARD_SIZE for _ in range(BOARD_SIZE)])
i_player = 2 # player 1 start fist
anyone_win = False

while not anyone_win:
    i_player = 2 if i_player == 1 else 1
    state, x, y = random_step(state, i_player)
    if x<0 or y<0:
        anyone_win, msg = False, 'No one wins.'
        break
    anyone_win, msg = check_winner(state)
    historical_states.append(slicer(state))
    historical_moves.append([i_player, x,y])

print state
print msg
print ''.join([str(i) if i != 9 else '|' for i in slicer(state)])

# print historical_states
print historical_moves
