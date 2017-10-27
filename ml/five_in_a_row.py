import random
import numpy as np
import copy
#import sklearn
from sklearn.neural_network import MLPClassifier

Learner = MLPClassifier(activation='relu', alpha=0.0001, batch_size='auto', beta_1=0.9,
       beta_2=0.999, early_stopping=False, epsilon=1e-08,
       hidden_layer_sizes=(100,50,30,20), learning_rate='constant',
       learning_rate_init=0.001, max_iter=500, momentum=0.9,
       nesterovs_momentum=True, power_t=0.5, random_state=None,
       shuffle=True, solver='adam', tol=0.0001, validation_fraction=0.1,
       verbose=False, warm_start=False)

LEARNER_FLAG_INIT = -100
Learner_flag = LEARNER_FLAG_INIT

BOARD_SIZE = 11
BOARD_SIZEm1 = BOARD_SIZE-1
BLOCKER = 9

traing_X = []
traing_Y = []

def random_step(in_state, player):
    global Learner_flag
    global Learner
    offset_x, offset_y = 0,0
    if Learner_flag > 0:
        n = Learner.predict(slicer(in_state))
        # print 'predicted {}'.format(n)

    while 0 in in_state:
        if Learner_flag > 0:
            x,y = number2location(n)
            x,y = x+offset_x,y+offset_y
            
            if x<0: x = 0
            if x>BOARD_SIZEm1: x = BOARD_SIZEm1
            if y<0: y = 0
            if y>BOARD_SIZEm1: y = BOARD_SIZEm1
            
            if in_state[x,y] == 0:
                in_state[x,y] = player
                return in_state, x, y
            else:
                offset_x += random.randint(-1,1)
                offset_y += random.randint(-1,1)
        else:
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
        return 1
    if 50 in states:
        return 2
    return 0


def location2number(x,y):
    return int(x+0.5)*BOARD_SIZE + int(y+0.5)

def number2location(n):
    ni = int(n+0.5)
    return ni/BOARD_SIZE,ni%BOARD_SIZE


def runner():
    historical_states = []
    historical_moves = []
    
    state = np.array([[0]*BOARD_SIZE for _ in range(BOARD_SIZE)])
    i_player = 2 # player 1 start fist
    winner = 0
    
    while True:
        i_player = 2 if i_player == 1 else 1
        state, x, y = random_step(state, i_player)
        # print '{2} putting in at location {0},{1}'.format(x,y, i_player)
        if x<0 or y<0:
            winner = 0
            break
        winner = check_winner(state)
        msg = 'Player {} wins.'.format(winner) if winner else 'No one wins.'
        historical_states.append(slicer(state))
        historical_moves.append([i_player, x,y])
        if winner:
            break
    
    historical_records = zip(historical_states, historical_moves)
    
    global traing_X
    global traing_Y
    global Learner_flag
    global Learner

    traing_X.extend([r[0] for r in historical_records if r[1][0] == winner])
    traing_Y.extend([location2number(r[1][1],r[1][2]) for r in historical_records if r[1][0] == winner])

    if Learner_flag > 0:
        Learner = Learner.fit(traing_X, traing_Y)
        # print 'Later:', Learner
    else:
        if Learner_flag == LEARNER_FLAG_INIT:
            Learner = Learner.fit(traing_X, traing_Y)
        Learner_flag += 1
        # print 'Init:', Learner
        
    state_present = copy.deepcopy(state)
    state_present[historical_moves[-1][1], historical_moves[-1][2]] = -state_present[historical_moves[-1][1], historical_moves[-1][2]]
    if Learner_flag % 100 == 0:
        print state_present
        print msg
        print ''.join([str(i) if i != 9 else '|' for i in slicer(state)])
        print historical_moves

for i in range(-LEARNER_FLAG_INIT + 301):
    runner()
