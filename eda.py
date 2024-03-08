# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 11:36:29 2024

@author: zarth
"""

import pandas as pd

path = "../airline_data/2019_06.csv"

data = pd.read_csv(path)

"""
TODO:
    make graph of connections
    calc metrics on each connection
    calc graph metrics for each node (airport) and edge(flight)
"""

### compute number of flights between all pairs of airports
data[["ORIGIN_AIRPORT_SEQ_ID", "DEST_AIRPORT_SEQ_ID"]].head()
origin_dest_pairs = data[["ORIGIN_AIRPORT_SEQ_ID", "DEST_AIRPORT_SEQ_ID"]]
flights_dict = origin_dest_pairs.groupby(["ORIGIN_AIRPORT_SEQ_ID", "DEST_AIRPORT_SEQ_ID"]).groups

flight_counts = []
for flight, value in flights_dict.items():
    flight_pair = sorted(flight)
    if type(value) == int:
        if not (*flight_pair, value) in flight_counts:
            flight_counts.append((*flight_pair, value))
    else:
        length = len(value)
        if not (*flight_pair, length) in flight_counts:
            flight_counts.append((*flight_pair, length))



