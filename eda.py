# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 11:36:29 2024

@author: zarth
"""

import pandas as pd
import matplotlib.pyplot as plt

path = "../airline_data/2019_06.csv"

data = pd.read_csv(path)
keep = ["MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", "FL_DATE", "MKT_UNIQUE_CARRIER",
        "ORIGIN_AIRPORT_ID", "ORIGIN", "DEST_AIRPORT_ID", "DEST", "CRS_DEP_TIME",
        "DEP_TIME", "DEP_DELAY", "TAXI_OUT", "WHEELS_OFF", "WHEELS_ON", "TAXI_IN",
        "CRS_ARR_TIME", "ARR_TIME", "ARR_DELAY", "CANCELLED", "CANCELLATION_CODE",
        "DIVERTED", "DUP", "CRS_ELAPSED_TIME", "ACTUAL_ELAPSED_TIME", "AIR_TIME", 
        "DISTANCE", "CARRIER_DELAY", "WEATHER_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]

data = data[keep]

"""
TODO:
    make graph of connections
    calc metrics on each connection
    calc graph metrics for each node (airport) and edge(flight)
"""

### compute number of flights between all pairs of airports
data[["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]].head()
origin_dest_pairs = data[["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]]
flights_dict = origin_dest_pairs.groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]).groups

flight_counts = []
for flight, value in flights_dict.items():
    if type(value) == int:
        if not (*flight, value) in flight_counts:
            flight_counts.append((*flight, value))
    else:
        length = len(value)
        if not (*flight, length) in flight_counts:
            flight_counts.append((*flight, length))

flight_counts.sort(reverse = True, key=lambda x: x[2])


x = list(flights_dict.keys())
x = x[0]
y = data.iloc[flights_dict[x]]
n = y.shape[0]

# distribution of arrival and departure delays
y["DEP_DELAY"].describe()
y["ARR_DELAY"].describe()

fig1, ax1 = plt.subplots(1, 2, sharey=True, tight_layout = True)
ax1[0].hist(y["DEP_DELAY"])
ax1[1].hist(y["ARR_DELAY"])
plt.show()

# percent delayed and cancelled
dep_delays = y[y["DEP_DELAY"] > 0].shape[0]
arr_delays = y[y["ARR_DELAY"] > 0].shape[0]

dep_delay_pct = dep_delays/n
arr_delay_pct = arr_delays/n

cancelled = y[y["CANCELLED"] == 1].shape[0]
cancelled_pct = cancelled/n


# distribution of overall delays
y.loc[:, "OVERALL_DELAY"] = y.apply(lambda x: x["ACTUAL_ELAPSED_TIME"] - x["CRS_ELAPSED_TIME"], axis = 1) 
y["OVERALL_DELAY"].describe()

fig2, ax2 = plt.subplots(1, 1)
ax2.hist(y["OVERALL_DELAY"])
plt.show()

# delay type breakdown (NOTE: not all delays have a reason recorded)
delay_types = ["CARRIER_DELAY", "WEATHER_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]

z = y[delay_types].dropna()
record_count = z.shape[0]

avg_sizes = []
type_percents = []
for delay_type in delay_types:
    delay_rows = z[z[delay_type] > 0]
    type_count = delay_rows.shape[0]
    if type_count != 0:
        avg_sizes.append(delay_rows[delay_type].mean())
        type_percents.append(delay_rows.shape[0]/record_count*100)
    else:
        avg_sizes.append(0)
        type_percents.append(0)

type_labels = ["Car", "Wth", "Sec", "Late"]        
fig3, ax3 = plt.subplots(1, 2)
ax3[0].bar(type_labels, avg_sizes)
ax3[1].bar(type_labels, type_percents)
plt.show()