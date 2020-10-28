#import yahoo_finance as yhf
import yfinance as yhf
from sklearn import *
import os.path, os, sys
import pickle
import numpy as np
import datetime as dt
# import pandas as pd

def next_biz_day(d):
    nd = d+dt.timedelta(days=1)
    return nd if nd.weekday() in range(5) else next_biz_day(nd)

def prev_biz_day(d):
    pd = d-dt.timedelta(days=1)
    return pd if pd.weekday() in range(5) else prev_biz_day(pd)

def get_raw(s_name, start, end):
    FILE_PATH, PATH_SEPERATOR = (os.environ.get('TEMP'), '\\') if sys.platform.startswith('win') else (r'/tmp', '/')
    file_name = FILE_PATH + PATH_SEPERATOR + s_name + start + end + '.txt'
    if os.path.isfile(file_name):
        with open(file_name,'r') as f:
            raw = pickle.load(f)
    else:
        #raw = yhf.Share(s_name).get_historical(start,end)
        raw = yhf.Ticker(s_name).history(start=start,end=start)
        # sample: yhf.Ticker('AAPL').history(start='2020-01-01',end='2020-10-27') 
        with open(file_name,'w') as f:
            pickle.dump(raw, f)
    return raw

def get_s(s_name, start, end, field):
    #return [float(i[field]) for i in get_raw(s_name, start, end)][::-1]
    return [float(i) for i in get_raw(s_name, start, end)['Close']][::-1]

def get_str(s_name, start, end, field):
    return [str(i[field]) for i in get_raw(s_name, start, end)][::-1]
    
def get_diff(arr):
    return [0] + [2.0*(arr[i+1] - arr[i])/(arr[i+1] + arr[i]) for i in range(len(arr) - 1)]

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-1.0 * z))

def nomalize(arr):
    x = np.array(arr)
    min, max = x[np.argmin(x)], x[np.argmax(x)]
    return ((x - min) / (max - min))*2.0 -1

def average(arr, ndays):
    a = [[arr[0]] * i + arr[:-i] if i>0 else arr for i in range(ndays)]
    k = np.zeros_like(a[0])
    for i in range(ndays):
        k += np.array(a[i])
    return np.array(k) / float(ndays)

def ave_n(n):
    return lambda x:average(x,  n)

def offset(arr, ndays):
    a = [arr[0]] * ndays + arr[:-ndays]
    return np.array(a)

def offset_n(n):
    return lambda x:offset(x,  n)

def merge_fs(fs):
    return fs[0] if len(fs) == 1 else lambda *args: (merge_fs(fs[1:]))(fs[0](*args))

# --- Run parameters ---

x_names = 'MSFT|AAPL|GOOG|FB|INTC|AMZN|BIDU'.split('|')
y_name = 'BIDU'
percentage_for_training = 0.95

se_dates = [dt.datetime(*d) for d in [(2013,1,3), (2017,10,20)]]
print (se_dates)
input_start,   input_end   = [d.strftime('%Y-%m-%d') for d in se_dates]
se_dates = [next_biz_day(d) for d in se_dates]
print se_dates
predict_start, predict_end = [d.strftime('%Y-%m-%d') for d in se_dates]

# training dataset selection
lwfs = [
    # label,   weight, methods
    ('Close',  2.0,    [get_s,                      nomalize, sigmoid]),
    ('Close',  5.0,    [get_s,            get_diff, nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, get_diff, offset_n(1), nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, get_diff, offset_n(2), nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, get_diff, offset_n(3), nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, get_diff, offset_n(4), nomalize, sigmoid]),
    ('Open',   3.0,    [get_s,            get_diff, nomalize, sigmoid]),
    ('High',   2.0,    [get_s,            get_diff, nomalize, sigmoid]),
    ('Low',    2.0,    [get_s,            get_diff, nomalize, sigmoid]),
    ('Volume', 1.0,    [get_s,                      nomalize, sigmoid]),
    ('Volume', 1.0,    [get_s, ave_n(5),            nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, ave_n(2),  get_diff, nomalize, sigmoid]),
    ('Open',   1.0,    [get_s, ave_n(2),  get_diff, nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, ave_n(3),  get_diff, nomalize, sigmoid]),
    ('Open',   1.0,    [get_s, ave_n(3),  get_diff, nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, ave_n(5),  get_diff, nomalize, sigmoid]),
    ('Open',   1.0,    [get_s, ave_n(5),  get_diff, nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, ave_n(10), get_diff, nomalize, sigmoid]),
    ('Open',   1.0,    [get_s, ave_n(10), get_diff, nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, ave_n(20), get_diff, nomalize, sigmoid]),
    ('Open',   1.0,    [get_s, ave_n(20), get_diff, nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, ave_n(30), get_diff, nomalize, sigmoid]),
    ('Open',   1.0,    [get_s, ave_n(30), get_diff, nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, ave_n(50), get_diff, nomalize, sigmoid]),
    ('Open',   1.0,    [get_s, ave_n(50), get_diff, nomalize, sigmoid]),
    ('Close',  1.0,    [get_s, ave_n(80), get_diff, nomalize, sigmoid]),
    ('Open',   1.0,    [get_s, ave_n(80), get_diff, nomalize, sigmoid]),
]

train_X_all = zip(*[w*(merge_fs(fs)(i, input_start, input_end, l)) for i in x_names for l,w,fs in lwfs])
train_Y_all = get_diff(get_s(y_name, predict_start, predict_end, 'Close'))
# train_Y_all_10 = [1 if i>0 else -1 for i in get_diff(get_s(y_name, predict_start, predict_end, 'Close'))]
xx1 =  get_str(y_name, predict_start, predict_end, 'Date')
xx2 =  get_s(y_name, predict_start, predict_end, 'Close')
print (zip(xx1,xx2)[-10:])

print ("Running for input X({0}) and Y({1})...".format(len(train_X_all), len(train_Y_all)))
if len(train_X_all) != len(train_Y_all):
    raise Exception("### Uneven input X({0}) and Y({1}), please Check!!!".format(len(train_X_all), len(train_Y_all)))

n_train_data = int(len(train_X_all)*percentage_for_training)
train_X, train_Y = train_X_all[30:n_train_data], train_Y_all[30:n_train_data]
test_X,  test_Y  = train_X_all[n_train_data:], train_Y_all[n_train_data:]

# fit and predict
def fit_and_predict(sklnr, train_X, train_Y, test_X):
    sklnr.fit(train_X ,train_Y)
    out_Y = sklnr.predict(test_X)
    actual_vs_predict = zip(*[test_Y, out_Y])
    matched_count = [1 if i[0]*i[1]>0 else 0 for i in actual_vs_predict]
    accuracy = 1.0* sum(matched_count)/len(matched_count)
    print ( 'Accuracy: {0}% Train({1}):Test({2}) - Model: {3}'.format(
        int(accuracy*1000)/10.0,
        len(train_Y),
        len(test_Y),
        str(sklnr).replace('\n','')[:140]) )
    print ( 'output: {}'.format(actual_vs_predict[-10:]) )

# choose different learners
learner = [
        # naive_bayes.GaussianNB(),
        # linear_model.SGDClassifier(),
        # svm.SVC(),
        # tree.DecisionTreeClassifier(),
        # ensemble.RandomForestClassifier(),
        ensemble.AdaBoostRegressor(),
        ensemble.BaggingRegressor(),
        ensemble.ExtraTreesRegressor(),
        ensemble.GradientBoostingRegressor(),
        ensemble.RandomForestRegressor(),
        gaussian_process.GaussianProcessRegressor(),
        linear_model.HuberRegressor(),
        linear_model.PassiveAggressiveRegressor(),
        linear_model.RANSACRegressor(),
        linear_model.SGDRegressor(),
        linear_model.TheilSenRegressor(),
        # multioutput.MultiOutputRegressor(),
        neighbors.KNeighborsRegressor(),
        neighbors.RadiusNeighborsRegressor(),
        neural_network.MLPRegressor(),
        tree.DecisionTreeRegressor(),
        tree.ExtraTreeRegressor(),
        ### linear_model.SGDRegressor(),
        ### tree.DecisionTreeRegressor(),
        ### ensemble.RandomForestRegressor(),
        ### neural_network.MLPRegressor(activation='tanh', solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(15, 2), random_state=1)
        # neural_network.MLPClassifier(activation='tanh', solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(15, 2), random_state=1)
    ]

# run
for l in learner:
    try:
        fit_and_predict(l, train_X, train_Y, test_X)
    except:
        pass
