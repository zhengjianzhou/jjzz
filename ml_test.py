import yahoo_finance as yhf
from sklearn import *

def get_s(s_name, start, end):
    x = yhf.Share(s_name)
    return [float(i['Close']) for i in x.get_historical(start,end)]
    
def get_diff(arr):
    a = []
    for i in range(len(arr) - 1):
        a.append(2.0*(arr[i+1] - arr[i])/(arr[i+1] + arr[i]))
    return [0] + a

x_names = 'MSFT|AAPL|GOOG|FB|TXN|INTC|AMZN'.split('|')
y_name = 'BIDU'

input_start, input_end = '2010-01-04', '2017-04-03'
predict_start, predict_end = '2010-01-05', '2017-04-04'

train_X_all = zip(*[get_diff(get_s(i, input_start, input_end)) for i in x_names])
train_Y_all = [1 if i>0 else 0 for i in get_diff(get_s(y_name, predict_start, predict_end))]

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

learner = [ tree.DecisionTreeClassifier(), naive_bayes.GaussianNB(), svm.SVC()]

for l in learner:
    fit_and_predict(l, train_X, train_Y, test_X)
