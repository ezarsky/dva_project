import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Range1d, Select

# uncomment to work in jupyter notebook, use "show" to see results
#from bokeh.io import output_notebook
#output_notebook()

# import data and lookup table for airport codes
data_path = "../airline_data/2019_06.csv"
iata_dot_code_path = "../airline_data/iata_to_dot_codes.csv"

data = pd.read_csv(data_path)
keep = ["MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", "FL_DATE", "MKT_UNIQUE_CARRIER",
        "ORIGIN_AIRPORT_ID", "ORIGIN", "DEST_AIRPORT_ID", "DEST", "CRS_DEP_TIME",
        "DEP_TIME", "DEP_DELAY", "TAXI_OUT", "WHEELS_OFF", "WHEELS_ON", "TAXI_IN",
        "CRS_ARR_TIME", "ARR_TIME", "ARR_DELAY", "CANCELLED", "CANCELLATION_CODE",
        "DIVERTED", "DUP", "CRS_ELAPSED_TIME", "ACTUAL_ELAPSED_TIME", "AIR_TIME", 
        "DISTANCE", "CARRIER_DELAY", "WEATHER_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]

data = data[keep]

code_lookup = pd.read_csv(iata_dot_code_path)

# get list of all pairs of airports
origin_dest_pairs = data[["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]]
flights_dict = origin_dest_pairs.groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]).groups
flight_pairs_dot = list(flights_dict.keys())

# TODO: incorporate city and airport names in menu of airport options

# create menu of airport options
from_airports = sorted(list(pd.unique(data["ORIGIN"].dropna())))
to_airports = sorted(list(pd.unique(data["DEST"].dropna())))

# create interactive selectors in bokeh
from_select = Select(title="Where from?", options=from_airports, value="DFW")
to_select = Select(title="Where to?", options=to_airports, value="IAH")

# create labels for plots and data filtering
pct_labels = ["Departure Delay", "Arrival Delay", "Cancelled"]
delay_types = ["CARRIER_DELAY", "WEATHER_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]
type_plot_labels = ["Car", "Wth", "Sec", "Late"]

# create ColumnDataSources for each plot 
dep_source = ColumnDataSource(data = dict(
        top_locs = [],
        left_locs = [],
        right_locs = []       
    ))

arr_source = ColumnDataSource(data = dict(
        top_locs = [],
        left_locs = [],
        right_locs = []
    ))

pct_source = ColumnDataSource(data = dict(
        labels = [],
        top_locs = []
    ))

ovr_source = ColumnDataSource(data = dict(
        top_locs = [],
        left_locs = [],
        right_locs = []
    ))

size_source = ColumnDataSource(data = dict(
        labels = [],
        top_locs = []
    ))

type_pct_source = ColumnDataSource(data = dict(
        labels = [],
        top_locs = []
    ))

# initialize all plot areas
w = 300
h = 250
dep_plot = figure(width = w, height = h)
dep_plot.quad(top="top_locs", bottom=0, left="left_locs", right="right_locs",
              source = dep_source, fill_color="green", line_color="white")
dep_plot.y_range.start = 0
dep_plot.xaxis.axis_label = "Delay time (minutes)"
dep_plot.yaxis.axis_label = "Frequency"

arr_plot = figure(width = w, height = h)
arr_plot.quad(top="top_locs", bottom=0, left="left_locs", right="right_locs", 
              source=arr_source, fill_color="blue", line_color="white")
arr_plot.y_range.start = 0
arr_plot.xaxis.axis_label = "Delay time (minutes)"
arr_plot.yaxis.axis_label = "Frequency"

pct_plot = figure(width = w, height = h, 
                  x_range=pct_labels, y_range=Range1d(0, 100))
pct_plot.vbar(x="labels", top="top_locs", source = pct_source, 
              fill_color="indigo", line_color="white", width = 0.8)
pct_plot.xaxis.axis_label = "Delay/Cancellation"
pct_plot.yaxis.axis_label = "% of flights on route delayed/cancelled"

ovr_plot = figure(width = w, height = h)
ovr_plot.quad(top="top_locs", bottom=0, left="left_locs", right="right_locs",
              source=ovr_source, fill_color="maroon", line_color="white")
ovr_plot.y_range.start=0
ovr_plot.xaxis.axis_label = "Delay time (minutes)"
ovr_plot.yaxis.axis_label = "Frequency"

size_plot = figure(width = w, height = h, x_range=type_plot_labels)
size_plot.vbar(x="labels", top="top_locs", source=size_source, 
               fill_color="tomato", line_color="white", width=0.8)
size_plot.y_range.start = 0
size_plot.xaxis.axis_label = "Type of Delay"
size_plot.yaxis.axis_label = "Average size of delay type (minutes)"

type_pct_plot = figure(width = w, height = h, x_range=type_plot_labels)
type_pct_plot.vbar(x="labels", top="top_locs", source=type_pct_source, 
                   fill_color="cyan", line_color="white", width=0.8)
type_pct_plot.y_range.start = 0
type_pct_plot.xaxis.axis_label = "Type of Delay"
type_pct_plot.yaxis.axis_label = "% of delayed flights with delay type"

# function for filtering data to only selected origin and destination
def select_flights():
    from_dot = int(code_lookup.loc[code_lookup["Code_iata"] == from_select.value, "Code_dot"].values[0])
    to_dot = int(code_lookup.loc[code_lookup["Code_iata"] == to_select.value, "Code_dot"].values[0])    
    selection_data = data.iloc[flights_dict[(from_dot, to_dot)]]
    return selection_data

# function for updating data sources based on selections
def update():
    selection_data = select_flights()
    n = selection_data.shape[0]
    # update departure delay data
    dep_hist, dep_edges = np.histogram(selection_data["DEP_DELAY"].dropna())
    dep_source.data = dict(
        top_locs = dep_hist,
        left_locs = dep_edges[:-1],
        right_locs = dep_edges[1:]
        )
    
    # update arrival delay data
    arr_hist, arr_edges = np.histogram(selection_data["ARR_DELAY"].dropna())
    arr_source.data = dict(
        top_locs = arr_hist,
        left_locs = arr_edges[:-1],
        right_locs = arr_edges[1:]
        )

    # update percent delayed and cancelled
    dep_delays = selection_data[selection_data["DEP_DELAY"] > 0].shape[0]
    arr_delays = selection_data[selection_data["ARR_DELAY"] > 0].shape[0]

    dep_delay_pct = dep_delays/n*100
    arr_delay_pct = arr_delays/n*100

    cancelled = selection_data[selection_data["CANCELLED"] == 1].shape[0]
    cancelled_pct = cancelled/n*100

    pct_heights = [dep_delay_pct, arr_delay_pct, cancelled_pct]
    pct_source.data = dict(
            labels = pct_labels,
            top_locs = pct_heights
        )

    # update overall delay data
    selection_data.loc[:, "OVERALL_DELAY"] = selection_data.apply(lambda x: x["ACTUAL_ELAPSED_TIME"] - x["CRS_ELAPSED_TIME"], axis = 1) 

    ovr_hist, ovr_edges = np.histogram(selection_data["OVERALL_DELAY"].dropna())
    ovr_source.data = dict(
        top_locs = ovr_hist,
        left_locs = ovr_edges[:-1],
        right_locs = ovr_edges[1:]
        )

    # update delay type breakdown (NOTE: not all delays have a reason recorded)
    type_data = selection_data[delay_types].dropna()
    record_count = type_data.shape[0]

    avg_sizes = []
    type_percents = []
    for delay_type in delay_types:
        delay_rows = type_data[type_data[delay_type] > 0]
        type_count = delay_rows.shape[0]
        if type_count != 0:
            avg_sizes.append(delay_rows[delay_type].mean())
            type_percents.append(delay_rows.shape[0]/record_count*100)
        else:
            avg_sizes.append(0)
            type_percents.append(0)

    size_source.data = dict(
            labels = type_plot_labels,
            top_locs = avg_sizes
        )
    type_pct_source.data = dict(
            labels = type_plot_labels,
            top_locs = type_percents
        )


# link select tools to update function
controls = [from_select, to_select]
for control in controls:
    control.on_change("value", lambda attr, old, new: update())

# create layout
dash_layout = layout(
    [
        [from_select, to_select],
        [dep_plot, arr_plot],
        [pct_plot, ovr_plot],
        [size_plot, type_pct_plot]
    ], 
    sizing_mode="stretch_width")

# initialize data based on default parameters
update()

# add layout to current document
curdoc().add_root(dash_layout)

