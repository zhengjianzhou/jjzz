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

BOARD_SIZE = 11
BOARD_SIZEm1 = BOARD_SIZE-1
BLOCKER = 9

MC_GUESS_SIZE = 50

traing_X = []
traing_Y = []

def mc_tree_search(in_state, player, depth):
    score = 0
    x, y = 0,0
    state = in_state
    global Learner
    
    empties = sum([list(i).count(0) for i in in_state])
    mc_size = min(empties,MC_GUESS_SIZE)
    
    for i in range(mc_size):
        i_state = copy.deepcopy(in_state)
        if depth <= 0:
            i_state, i_x, i_y = random_step(i_state, player)
            i_score = Learner.predict(slicer(i_state))[0]
            print "predicted:  i_x, i_y i_score",  i_x, i_y, i_score
        else:
            i_state, i_x, i_y, i_score = mc_tree_search(i_state, player, depth-1)
            
        if i_score > score:
            state = i_state
            score = i_score
            x, y = i_x, i_y
            
    print "###player, depth, x, y, score", player, depth, x, y, score
    return state, x, y, score

def random_step_adpator(in_state, player, _depth):
    in_state, x, y =  random_step(in_state, player)
    return in_state, x, y, 0

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
        return 1
    if 50 in states:
        return 2
    return 0


def location2number(x,y):
    return int(x+0.5)*BOARD_SIZE + int(y+0.5)

def number2location(n):
    ni = int(n+0.5)
    return ni/BOARD_SIZE,ni%BOARD_SIZE


def runner(f_next_step, rounds = 100, depth=0, skip_print = 1):
    for i_round in range(rounds):
        historical_states, historical_moves, historical_msgs = [], [], []
        state = np.array([[0]*BOARD_SIZE for _ in range(BOARD_SIZE)])
        i_player, winner = 2, 0 # player 1 start fist
        
        while True:
            i_player = 2 if i_player == 1 else 1
            state, x, y, _ = f_next_step(state, i_player, depth)
            if x<0 or y<0:
                winner = 0
                break
            winner = check_winner(state)
            msg = 'Player {} wins.'.format(winner) if winner else 'No one wins.'
            historical_states.append(slicer(state))
            historical_moves.append([i_player, x,y])
            historical_msgs.append(msg)
            if winner:
                break
        
        historical_records = zip(historical_states, historical_moves, historical_msgs)

        global traing_X, traing_Y
        traing_X.extend([r[0] for r in historical_records])
        traing_Y.extend([1 if r[1][0] == winner else 0 for r in historical_records])
    
        state_present = copy.deepcopy(state)
        state_present[historical_moves[-1][1], historical_moves[-1][2]] = -state_present[historical_moves[-1][1], historical_moves[-1][2]]
        if i_round % skip_print == 0:
            print state_present, msg, historical_moves
            print ''.join([str(i) if i != 9 else '|' for i in slicer(state)])    
        

runner(random_step_adpator, 1000, 0, 1000)
print '### Finished 300 runs.'
Learner = Learner.fit(traing_X, traing_Y)
print traing_X[:2]
print traing_Y[:2]
print '### Fitted with learner.'
runner(mc_tree_search, 1, 1)
