import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error as mse
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

path = "../airline_data/2019top30data.csv"

data = pd.read_csv(path, low_memory=False)

"""
TODO:
    Tune RF model
    Integrate model results into interactive file
"""


df = data.dropna(subset='OVERALL_DELAY')
origin_cols = ["ORIGIN_AIRPORT_ID"]
dest_cols = ["DEST_AIRPORT_ID"]

delay_stats = df["OVERALL_DELAY"].describe()
delay_iqr = delay_stats["75%"] - delay_stats["25%"]
outlier_fences = [delay_stats["25%"] - 1.5 * delay_iqr,  delay_stats["75%"] + 1.5 * delay_iqr]
df = df[df["OVERALL_DELAY"] > outlier_fences[0]]
df = df[df["OVERALL_DELAY"] < outlier_fences[1]]

sample = df.sample(n=1000, random_state=1)


# binary recoding of airport codes
"""
def recode_id(airport_id):
    binary = list(bin(airport_id)[2:]) 
    binary = [int(bit) for bit in binary]
    return binary

sample.loc[:, "ORIGIN_BIN"] = sample["ORIGIN_AIRPORT_ID"].apply(recode_id)
sample.loc[:, "DEST_BIN"] = sample["DEST_AIRPORT_ID"].apply(recode_id)
origin_cols = ["ORIGIN_BIN_" + str(i+1) for i in range(14)]
dest_cols = ["DEST_BIN_" + str(i+1) for i in range(14)]

for i, col in enumerate(origin_cols):
    sample.loc[:, col] = sample["ORIGIN_BIN"].apply(lambda x: x[i])
for i, col in enumerate(dest_cols):
    sample.loc[:, col] = sample["DEST_BIN"].apply(lambda x: x[i])
"""
#Xtrain = df[["MONTH",'DAY_OF_MONTH','ORIGIN_AIRPORT_ID','DEST_AIRPORT_ID']]
#ytrain = np.ravel(df[['DEP_DELAY']])

X = sample[["MONTH",'DAY_OF_MONTH'] + origin_cols + dest_cols]
y = np.ravel(sample[['OVERALL_DELAY']])


"""
X["MONTH"].corr(sample["OVERALL_DELAY"])
X["DAY_OF_MONTH"].corr(sample["OVERALL_DELAY"])
plt.scatter(X["MONTH"], y)
plt.show()
plt.scatter(X["DAY_OF_MONTH"], y)
plt.show()
"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1) 

"""
top_depth = 15
max_depths = list(range(1, top_depth))
train_errors = []
test_errors = []

for depth in max_depths:
    print("Training random forest with maximum depth of {}".format(depth))
    rf = RandomForestRegressor(random_state=1, max_depth=depth)
    rf.fit(X_train, y_train)
    preds_train = rf.predict(X_train)
    preds_test = rf.predict(X_test)    
    train_errors.append(mse(y_train, preds_train))
    test_errors.append(mse(y_test, preds_test))

fig, ax = plt.subplots()
ax.plot(max_depths, train_errors, color="blue")
ax.plot(max_depths, test_errors, color="red")
plt.show()

depth_opt = max_depths[np.argmin(test_errors)]

max_trees = 1000
n_trees = list(range(50, max_trees, 50))
train_errors = []
test_errors = []

for count in n_trees:
    print("Training random forest with {} trees".format(count))
    rf = RandomForestRegressor(n_estimators=count, random_state=1)
    rf.fit(X_train, y_train)
    preds_train = rf.predict(X_train)
    preds_test = rf.predict(X_test)    
    train_errors.append(mse(y_train, preds_train))
    test_errors.append(mse(y_test, preds_test))

fig, ax = plt.subplots()
ax.plot(n_trees, train_errors, color="blue")
ax.plot(n_trees, test_errors, color="red")
plt.show()

n_trees_opt = n_trees[np.argmin(test_errors)]

m_vals = [i / 4 for i in range(1, 5)]
train_errors = []
test_errors = []

for m in m_vals:
    print("Training random forest with m={}".format(m))
    rf = RandomForestRegressor(max_features=m, random_state=1)
    rf.fit(X_train, y_train)
    preds_train = rf.predict(X_train)
    preds_test = rf.predict(X_test)    
    train_errors.append(mse(y_train, preds_train))
    test_errors.append(mse(y_test, preds_test))

fig, ax = plt.subplots()
ax.plot(m_vals, train_errors, color="blue")
ax.plot(m_vals, test_errors, color="red")
plt.show()

m_opt = m_vals[np.argmin(test_errors)]

depths = list(range(1, 11, 2))
n_trees = list(range(100, 200, 20))
m_vals = [i/4 for i in range(1, 5)]
hyper_param_list = []
train_errors = []
test_errors = []

for depth in depths:
    for count in n_trees:
        for m in m_vals:
            print("Training random forest with depth={}, number of trees = {}, and m={}".format(depth, count, m))
            hyper_param_list.append((depth, count, m))
            rf = RandomForestRegressor(max_depth=depth,
                                       n_estimators = count, 
                                       max_features=m, 
                                       random_state=1)
            rf.fit(X_train, y_train)
            preds_train = rf.predict(X_train)
            preds_test = rf.predict(X_test)    
            train_errors.append(mse(y_train, preds_train))
            test_errors.append(mse(y_test, preds_test))

min_test_error = min(test_errors)
hyper_param_opt = hyper_param_list[np.argmin(test_errors)]
print("Optimal hyperparameter values:\n   depth={}\n    number of trees={}\n    m={}".format(*hyper_param_opt))
"""
# optimum values: depth = 1, number of trees = 120, m = 0.25
hyper_param_opt = (1, 120, 0.25)
build_rf = True
if build_rf:
    # build model
    X = df[["MONTH",'DAY_OF_MONTH'] + origin_cols + dest_cols]
    y = np.ravel(df[['OVERALL_DELAY']])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    
    rf = RandomForestRegressor(max_depth=hyper_param_opt[0],
                               n_estimators = hyper_param_opt[1], 
                               max_features=hyper_param_opt[2], 
                               random_state=1)
    rf.fit(X_train, y_train)
    
    # saves model to drive
    joblib.dump(rf,'rf_model.joblib',compress=3)

# read in model
rf_file = joblib.load('rf_model.joblib')

preds_train = rf.predict(X_train)
preds_test = rf.predict(X_test)

train_error = mse(y_train, preds_train)
test_error = mse(y_test, preds_test)

