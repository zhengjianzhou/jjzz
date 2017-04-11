import yahoo_finance as yhf
import sklearn as skl
from sklearn import *
import os.path
import pickle
import numpy as np

FILE_PATH = 'c:\\Temp\\SS\\'

def get_s(s_name, start, end, field):
    file_name = FILE_PATH + s_name + start + end + '.txt'
    if os.path.isfile(file_name):
        f = open(file_name,'r')
        raw = pickle.load(f)
        f.close()
    else:
        x = yhf.Share(s_name)
        raw = x.get_historical(start,end)
        f = open(file_name,'w')
        pickle.dump(raw, f)
        f.close()

    return [float(i[field]) for i in raw]
    
def get_diff(arr):
    a = []
    for i in range(len(arr) - 1):
        a.append(2.0*(arr[i+1] - arr[i])/(arr[i+1] + arr[i]))
    return [0] + a

def sigmoid(z):
        s = 1.0 / (1.0 + np.exp(-1.0 * z))
        return s

def nomalize(arr):
    xx = np.array(arr)
    max = xx[np.argmax(xx)]
    min = xx[np.argmin(xx)]
    xx = (xx - min) / (max - min)
    xxx = sigmoid(xx)
    return xxx

x_names = 'MSFT|AAPL|GOOG|FB|INTC|AMZN|BIDU'.split('|')
y_name = 'BIDU'

input_start, input_end = '2010-01-04', '2017-04-03'
# predict_start, predict_end = '2010-01-04', '2017-04-03'
predict_start, predict_end = '2010-01-05', '2017-04-04'

all_data = []
all_data += [nomalize(get_diff(get_s(i, input_start, input_end, 'Close'))) * 2.0 for i in x_names]
for t in 'Open|High|Low'.split('|'):
    all_data += [nomalize(get_diff(get_s(i, input_start, input_end, t))) for i in x_names]
all_data += [nomalize(get_s(i, input_start, input_end, 'Volume')) for i in x_names]
           
train_X_all = zip(*all_data)
train_Y_all = [1 if i>0 else 0 for i in get_diff(get_s(y_name, predict_start, predict_end, 'Close'))]

percentage_for_training = 0.95
n_train_data = int(len(train_X_all)*percentage_for_training)
train_X = train_X_all[:n_train_data]
test_X = train_X_all[n_train_data:]
train_Y = train_Y_all[:n_train_data]
test_Y = train_Y_all[n_train_data:]

def fit_and_predict(sklnr, train_X, train_Y, test_X):
    sklnr.fit(train_X ,train_Y)
    out_Y = sklnr.predict(test_X)
    
    real_and_predict = zip(*[test_Y, out_Y])
    matched_count = [1 if i[0]==i[1] else 0 for i in real_and_predict]
    accuracy = 1.0* sum(matched_count)/len(matched_count)
    print '{0} : Prediction accuracy: {1}'.format(sklnr, accuracy)

learner = [
        naive_bayes.GaussianNB(),
        linear_model.SGDClassifier(),
        svm.SVC(),
        tree.DecisionTreeClassifier(),
        ensemble.RandomForestClassifier(),
        # neural_network.MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(10, 2), random_state=1)
    ]

for l in learner:
    fit_and_predict(l, train_X, train_Y, test_X)
