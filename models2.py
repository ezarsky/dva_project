import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error as mse
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from timeit import default_timer as timer

path = "../airline_data/2019top30data2.parquet"

data = pd.read_parquet(path, engine="fastparquet")

df = data.dropna(subset='OVERALL_DELAY')

seasons = ["Winter", "Spring", "Summer", "Fall"]
airlines = sorted(list(df["AIRLINE"].unique()))

feature_cols = ["MONTH", "DAY_OF_MONTH","ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]
feature_cols += ["AIRLINE" + airline for airline in airlines]
feature_cols += seasons

delay_stats = df["OVERALL_DELAY"].describe()
delay_iqr = delay_stats["75%"] - delay_stats["25%"]
outlier_fences = [delay_stats["25%"] - 1.5 * delay_iqr,  delay_stats["75%"] + 1.5 * delay_iqr]
df = df[df["OVERALL_DELAY"] > outlier_fences[0]]
df = df[df["OVERALL_DELAY"] < outlier_fences[1]]

#sample = df.sample(n=1000, random_state=1)
#X = sample[feature_cols]
#y = np.ravel(sample[['OVERALL_DELAY']])


X = df[feature_cols]
y = np.ravel(df[['OVERALL_DELAY']])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)


"""
top_depth = 25
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
n_trees = list(range(25, max_trees, 25))
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

max_m = X.shape[1]
m_vals = [i / max_m for i in range(1, max_m)]
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

od_pairs = data[["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]]

flight_pairs_dict = od_pairs.groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]).groups
flight_pairs_dot = list(flight_pairs_dict.keys())


depths = list(range(1, 11, 2))
n_trees = list(range(100, 200, 20))
m_vals = [i/max_m for i in range(1, max_m, 3)]
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

# optimum values: depth = 10, number of trees = 100, m = 0.25
hyper_param_opt = (10, 100, 0.25)
build_rf = True
if build_rf:
    # build model
    X = df[feature_cols]
    y = np.ravel(df[['OVERALL_DELAY']])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    
    rf = RandomForestRegressor(max_depth=hyper_param_opt[0],
                               n_estimators=hyper_param_opt[1],
                               max_features=hyper_param_opt[2],
                               random_state=1, verbose = 10, n_jobs=-1)
    rf.fit(X_train, y_train)
    
    # saves model to drive
    start = timer()
    joblib.dump(rf,'rf_model.joblib',compress=3)
    end = timer()
    print(end-start)

# read in model
start = timer()
rf_file = joblib.load('rf_model.joblib')
end = timer()
print(end-start)


# get list of all pairs of airports
od_pairs = df[["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]]
flight_pairs_dict = od_pairs.groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]).groups
flight_pairs_dot = list(flight_pairs_dict.keys())


preds_train = rf.predict(X_train)
preds_test = rf.predict(X_test)

train_error = mse(y_train, preds_train)
test_error = mse(y_test, preds_test)

