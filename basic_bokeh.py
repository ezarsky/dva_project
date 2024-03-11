#!/usr/bin/env python
# coding: utf-8

# In[41]:


import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.layouts import row
from bokeh.models import Dropdown, Range1d


# In[2]:


output_notebook()


# In[3]:


path = "../airline_data/2019_06.csv"

data = pd.read_csv(path)
keep = ["MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", "FL_DATE", "MKT_UNIQUE_CARRIER",
        "ORIGIN_AIRPORT_ID", "ORIGIN", "DEST_AIRPORT_ID", "DEST", "CRS_DEP_TIME",
        "DEP_TIME", "DEP_DELAY", "TAXI_OUT", "WHEELS_OFF", "WHEELS_ON", "TAXI_IN",
        "CRS_ARR_TIME", "ARR_TIME", "ARR_DELAY", "CANCELLED", "CANCELLATION_CODE",
        "DIVERTED", "DUP", "CRS_ELAPSED_TIME", "ACTUAL_ELAPSED_TIME", "AIR_TIME", 
        "DISTANCE", "CARRIER_DELAY", "WEATHER_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]

data = data[keep]


# In[4]:


### compute number of flights between all pairs of airports
data[["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]].head()
origin_dest_pairs = data[["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]]
flights_dict = origin_dest_pairs.groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]).groups


# In[5]:


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


# In[6]:


x = list(flights_dict.keys())
x = x[0]
y = data.iloc[flights_dict[x]]
n = y.shape[0]


# In[36]:


# distribution of arrival and departure delays
print(y["DEP_DELAY"].describe())


dep_plot = figure(width = 400, height = 300)
dep_hist, dep_edges = np.histogram(y["DEP_DELAY"].dropna())
dep_plot.quad(top=dep_hist, bottom=0, left=dep_edges[:-1], right=dep_edges[1:], fill_color="green", line_color="white")
dep_plot.y_range.start = 0
dep_plot.xaxis.axis_label = "Delay time (minutes)"
dep_plot.yaxis.axis_label = "Frequency"

arr_plot = figure(width = 400, height = 300)
arr_hist, arr_edges = np.histogram(y["ARR_DELAY"].dropna())
arr_plot.quad(top=arr_hist, bottom=0, left=arr_edges[:-1], right=arr_edges[1:], fill_color="blue", line_color="white")
arr_plot.y_range.start = 0
arr_plot.xaxis.axis_label = "Delay time (minutes)"
arr_plot.yaxis.axis_label = "Frequency"

layout = row(dep_plot, arr_plot)
show(layout)


# In[38]:


# percent delayed and cancelled
dep_delays = y[y["DEP_DELAY"] > 0].shape[0]
arr_delays = y[y["ARR_DELAY"] > 0].shape[0]

dep_delay_pct = dep_delays/n*100
arr_delay_pct = arr_delays/n*100

cancelled = y[y["CANCELLED"] == 1].shape[0]
cancelled_pct = cancelled/n*100

pct_labels = ["Departure Delay", "Arrival Delay", "Cancelled"]
pct_heights = [dep_delay_pct, arr_delay_pct, cancelled_pct]
pct_plot = figure(width=400, height=300, x_range=pct_labels, y_range=Range1d(0, round(max(pct_heights) + 10, -1)))
pct_plot.vbar(x=pct_labels, top=pct_heights, fill_color="indigo", line_color="white", width = 0.8)
pct_plot.xaxis.axis_label = "Delay/Cancellation"
pct_plot.yaxis.axis_label = "% of flights on route delayed/cancelled"
show(pct_plot)


# In[39]:


# distribution of overall delays
y.loc[:, "OVERALL_DELAY"] = y.apply(lambda x: x["ACTUAL_ELAPSED_TIME"] - x["CRS_ELAPSED_TIME"], axis = 1) 
print(y["OVERALL_DELAY"].describe())

ovr_plot = figure(width=400, height=300)
ovr_hist, ovr_edges = np.histogram(y["OVERALL_DELAY"].dropna())
ovr_plot.quad(top=ovr_hist, bottom=0, left=ovr_edges[1:], right=ovr_edges[:-1], fill_color="maroon", line_color="white")
ovr_plot.y_range.start=0
ovr_plot.xaxis.axis_label = "Delay time (minutes)"
ovr_plot.yaxis.axis_label = "Frequency"
show(ovr_plot)


# In[40]:


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

size_plot = figure(width=400, height=300, x_range=type_labels)
size_plot.vbar(x=type_labels, top=avg_sizes, fill_color="tomato", line_color="white", width=0.8)
size_plot.y_range.start = 0
size_plot.xaxis.axis_label = "Type of Delay"
size_plot.yaxis.axis_label = "Average size of delay type (minutes)"

type_pct_plot = figure(width=400, height=300, x_range=type_labels)
type_pct_plot.vbar(x=type_labels, top=type_percents, fill_color="cyan", line_color="white", width=0.8)
type_pct_plot.y_range.start = 0
type_pct_plot.xaxis.axis_label = "Type of Delay"
type_pct_plot.yaxis.axis_label = "% of delayed flights with delay type"

layout = row(size_plot, type_pct_plot)
show(layout)


# In[46]:


from_dropdown = Dropdown(label="Where from?", button_type="warning", menu = ["Foo", "Bar", "Baz"])

show(from_dropdown)

