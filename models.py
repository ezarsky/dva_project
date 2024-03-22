import pandas as pd
import os 
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor

path = os.getcwd() + "/data/2019_06.csv"

data = pd.read_csv(path, low_memory=False)
keep = ["MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", "FL_DATE", "MKT_UNIQUE_CARRIER",
        "ORIGIN_AIRPORT_ID", "ORIGIN", "DEST_AIRPORT_ID", "DEST", "CRS_DEP_TIME",
        "DEP_TIME", "DEP_DELAY", "TAXI_OUT", "WHEELS_OFF", "WHEELS_ON", "TAXI_IN",
        "CRS_ARR_TIME", "ARR_TIME", "ARR_DELAY", "CANCELLED", "CANCELLATION_CODE",
        "DIVERTED", "DUP", "CRS_ELAPSED_TIME", "ACTUAL_ELAPSED_TIME", "AIR_TIME", 
        "DISTANCE", "CARRIER_DELAY", "WEATHER_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]

data = data[keep]

"""
TODO:
    Tune RF model
    Integrate model results into interactive file
"""


df = data.dropna(subset='DEP_DELAY')

Xtrain = df[["MONTH",'MKT_UNIQUE_CARRIER','ORIGIN_AIRPORT_ID','DEST_AIRPORT_ID']]
ytrain = np.ravel(df[['DEP_DELAY']])
 
# map airline names to numerical representation
names_to_numeric = {airline:i for i, airline in enumerate(Xtrain['MKT_UNIQUE_CARRIER'].unique())}

# change airline names from categorical to numeric
Xtrain.loc[:, 'MKT_UNIQUE_CARRIER'] = Xtrain['MKT_UNIQUE_CARRIER'].replace(names_to_numeric,inplace =False)

build_rf = False

if build_rf:
    # build model
    clf = RandomForestRegressor(random_state=10)
    clf = clf.fit(Xtrain, ytrain)
    # saves model to drive
    joblib.dump(clf,'rf_model.joblib',compress=3)

# read in model
rf_file = joblib.load('rf_model.joblib')

# example prediction
print(Xtrain.head(1))
print(rf_file.predict(Xtrain.head(1))[0], 'minute predicted dep-delay')
