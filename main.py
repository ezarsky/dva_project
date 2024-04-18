from bokeh.plotting import figure, from_networkx
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import (ColumnDataSource, DataTable, MultiLine, Range1d, 
                          Scatter, Select, StringFormatter, TableColumn)
import joblib
import networkx as nx
import numpy as np
import pandas as pd

###################
### Data Import ###
###################
# import data and lookup table for airport codes
data_path = "2019top30data.parquet"
lookup_path = "airport_lookup.csv"

data = pd.read_parquet(data_path, engine="fastparquet")
data = data.dropna()

code_lookup = pd.read_csv(lookup_path)

rf_model = joblib.load('rf_model.joblib')

#####################
### Data Cleaning ###
#####################

months = ["All", "Jan", "Feb", "Mar", "Apr",
          "May", "Jun", "Jul", "Aug",
          "Sep", "Oct", "Nov", "Dec"]

days = ["All"] + [str(i) for i in range(1, 32)]

seasons = ["Winter", "Spring", "Summer", "Fall"]
airlines = sorted(list(data["AIRLINE"].unique()))

feature_cols = ["MONTH", "DAY_OF_MONTH","ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]
feature_cols += ["AIRLINE" + airline for airline in airlines]
feature_cols += seasons

top_30_airports_iata = ["ATL", "DFW", "DEN", "ORD", "LAX",
                        "JFK", "LAS", "MCO", "MIA", "CLT",
                        "SEA", "PHX", "EWR", "SFO", "IAH",
                        "BOS", "FLL", "MSP", "LGA", "DTW",
                        "PHL", "SLC", "DCA", "SAN", "BWI",
                        "TPA", "AUS", "IAD", "BNA", "MDW"]

code_lookup = code_lookup[code_lookup["code_iata"].isin(top_30_airports_iata)]
code_lookup = code_lookup.drop_duplicates(subset = ["code_dot"])

# get list of all pairs of airports
od_pairs = data[["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]]
origin_counts = od_pairs.groupby("ORIGIN_AIRPORT_ID")["DEST_AIRPORT_ID"].count()
dest_counts = od_pairs.groupby("DEST_AIRPORT_ID")["ORIGIN_AIRPORT_ID"].count()
flight_counts = origin_counts + dest_counts
flight_counts = flight_counts.rename("flight_count")
flight_pairs_dict = od_pairs.groupby(["ORIGIN_AIRPORT_ID", "DEST_AIRPORT_ID"]).groups
flight_pairs_dot = list(flight_pairs_dict.keys())

# create menu of airport options
airports = []
flight_pairs = []
from_airports = []
to_airports = []

for pair in flight_pairs_dot:
    # create from_node dictionary whose values will be added to graph
    from_mask = code_lookup["code_dot"] == pair[0]
    from_row = code_lookup[from_mask]
    from_node = {
        "name": from_row["airport_name"].values[0],
        "iata_code": from_row["code_iata"].values[0],
        "city": from_row["city_name"].values[0],
        "geo_coords": (from_row["latitude"].values[0], 
                       from_row["longitude"].values[0]),
        "flight_count": flight_counts[pair[0]]
    }

    # create to_node dictionary whose values will be added to graph
    to_mask = code_lookup["code_dot"] == pair[1]
    to_row = code_lookup[to_mask]
    to_node = {
        "name": to_row["airport_name"].values[0],
        "iata_code": to_row["code_iata"].values[0],
        "city": to_row["city_name"].values[0],
        "geo_coords": (to_row["latitude"].values[0], 
                       to_row["longitude"].values[0]),
        "flight_count": flight_counts[pair[1]]
    }
    
    # join strings to create more complete airport name
    from_option = from_node["name"] + " (" + from_node["iata_code"] + ")"
    to_option = to_node["name"] + " (" + to_node["iata_code"] + ")"
    
    # add any new nodes to airports list    
    if not from_node in airports:
        airports.append(from_node)
    if not to_node in airports:
        airports.append(to_node)
    
    # add nodes to list of flight pairs that will become edges
    flight_pairs.append((from_node, to_node))
    from_airports.append(from_option)
    to_airports.append(to_option)

# sort list of airports (probably not different)
from_airports = sorted(list(set(from_airports)))
to_airports = sorted(list(set(to_airports)))

# initialize iata code for subsetting data
from_iata = from_airports[0][-4:-1]
to_iata = from_airports[1][-4:-1]


#####################
### Network Graph ###
#####################
#specify colors
bgcolor = "ghostwhite"
ddcolor = "midnightblue"
selected_edge_color = "#333333"
other_edge_color = "#dddddd"

# create Graph
airport_graph = nx.Graph()

# add nodes
for airport in airports:
    airport_graph.add_node(airport["iata_code"],
                           name = airport["iata_code"],
                           city = airport["city"],
                           pos=(airport["geo_coords"][1],
                                airport["geo_coords"][0]),
                           flight_count = airport["flight_count"])

# add edges
for pair in flight_pairs:
    airport_graph.add_edge(pair[0]["iata_code"], pair[1]["iata_code"])

# convert codes to integers for compatibility with bokeh
airport_graph = nx.convert_node_labels_to_integers(airport_graph, label_attribute="iata_code")

# get node positions for plotting with bokeh
pos = nx.get_node_attributes(airport_graph, 'pos')

##########################
### Interactive Visual ###
##########################
# plot and widget size parameters
figure_width = 800
network_w = int(0.75*figure_width)
network_h = network_w

drilldown_count = 3
w = int(0.35*figure_width)
h = int(network_h/drilldown_count)


# define size parameters for bokeh selectors
small_widget_count = 4
large_widget_count = 1
large_to_small = 2
widget_count = small_widget_count + large_to_small*large_widget_count
small_widget_width = int(figure_width/widget_count)
large_widget_width = int(figure_width/widget_count)

airlines = ["All"] + airlines

# create interactive selectors in bokeh
month_select = Select(title="Month", options = months, 
                     value = months[0], width = small_widget_width)

day_select = Select(title="Day", options = days, 
                     value = days[0], width = small_widget_width)

airline_select = Select(title="Airline", options = airlines, 
                     value = months[0], width = small_widget_width)

from_select = Select(title="Where from?", options=from_airports, 
                     value=from_airports[0], width=large_widget_width)

to_select = Select(title="Where to?", options=to_airports, 
                   value=from_airports[1], width=large_widget_width)


# create labels for plots and data filtering
pct_labels = ["Departure Delay", "Arrival Delay"]


# create ColumnDataSources for each plot 
# summary table data source
summary_data = dict(
        stat_names=["Number of flights", "Average Delay", 
                    "Shortest Delay Forecast", "Average Delay Forecast",
                    "Longest Delay Forecast", "Route Score"],
        stat_values=[0]*6
    )

sum_source = ColumnDataSource(data = summary_data)

# delay histogram data source
ovr_source = ColumnDataSource(data = dict(
        top_locs = [],
        left_locs = [],
        right_locs = []
    ))

# type of delay bar chart data source
pct_source = ColumnDataSource(data = dict(
        labels = [],
        top_locs = []
    ))

TOOLTIPS = [
    ("Airport", "@name"),
    ("City", "@{city}"),
    ("Flights in 2019", "@flight_count")
]



##################
### Plot Setup ###
##################
# initialize network plot
network_plot = figure(width = network_w, height = network_h, sizing_mode="fixed", 
                      x_axis_location=None, y_axis_location=None, toolbar_location=None,
                      title="Airport Network", background_fill_color=bgcolor,
                      tooltips=TOOLTIPS)
network_plot.grid.grid_line_color = None


# initialize summary data table plot
columns = [
        TableColumn(field="stat_names", title="", 
                    formatter=StringFormatter(font_style="bold")),
        TableColumn(field="stat_values", title="")
        
    ]

data_table = DataTable(source=sum_source, columns=columns, width=w, height=h,
                       index_position=None)


# initialize overall delays plot
ovr_plot = figure(width = w, height = h, sizing_mode="fixed", 
                  toolbar_location=None, title="Delay Lengths (minutes)",
                  background_fill_color=bgcolor, x_range=Range1d(-50, 150))
ovr_plot.quad(top="top_locs", bottom=0, left="left_locs", right="right_locs",
              source=ovr_source, fill_color=ddcolor, line_color="white")
ovr_plot.y_range.start=0
ovr_plot.xaxis.axis_label = "Delay time (minutes)"
ovr_plot.yaxis.axis_label = "Frequency"


# initialize percentage delayed/cancelled plot
pct_plot = figure(width = w, height = h, sizing_mode="fixed",
                  x_range=pct_labels, y_range=Range1d(0, 100),
                  toolbar_location=None, title="Percent Delayed",
                  background_fill_color=bgcolor)
pct_plot.vbar(x="labels", top="top_locs", source = pct_source, 
              fill_color=ddcolor, line_color="white", width = 0.8)
pct_plot.xaxis.axis_label = "Delay Type"
pct_plot.yaxis.axis_label = "% of flights on route"



# function for filtering data to only selected origin and destination
def route_score(avg_delay, std_delay, num_flights):
    route_scores = ["Good", "Fair", "Poor", "Insufficient Volume"]
    # return insufficient volume if less than 5 flights
    if num_flights < 5:
        return route_scores[3]  
    else:
        # set conditions for determining score
        short_delay = avg_delay < -5
        consistent = std_delay < 10
        # "Good" if both short and consistent
        if short_delay and consistent:
            return route_scores[0]
        # "Fair" if only short or only consistent
        elif short_delay or consistent:
            return route_scores[1]
        # "Poor" otherwise
        else:
            return route_scores[2]



# function for selecting data
def select_flights():
    # get values from selectors
    from_iata = from_select.value[-4:-1]
    to_iata = to_select.value[-4:-1]
    month = months.index(month_select.value)
    day = days.index(day_select.value)
    airline = airline_select.value
    
    # get dot codes that correspond to selected airports
    from_dot = int(code_lookup.loc[code_lookup["code_iata"] == from_iata, "code_dot"].values[0])
    to_dot = int(code_lookup.loc[code_lookup["code_iata"] == to_iata, "code_dot"].values[0])
    
    # handle case of same origin and destination (no update)
    if from_dot != to_dot:
        
        # filter data selection by values of selectors
        try:
            selection_data = data.loc[flight_pairs_dict[(from_dot, to_dot)]]
            if month != 0:
                selection_data = selection_data[selection_data["MONTH"] == month]

            if day != 0:
                selection_data = selection_data[selection_data["DAY_OF_MONTH"] == day]

            if airline != "All":
                selection_data = selection_data[selection_data["AIRLINE"] == airline]
            return selection_data
        
        # return nothing if KeyError occurs
        except:
            selection_data = pd.DataFrame(columns=data.columns)
            return selection_data



# function for updating data sources based on selections
def update():
    # handle case of same origin and destination (no update)
    from_iata = from_select.value[-4:-1]
    to_iata = to_select.value[-4:-1]
    selection_data = pd.DataFrame(columns=data.columns)
    if from_iata != to_iata:
        # if different origin and destination, call select_flights()
        selection_data = select_flights()
        
        # update network graph
        edge_attr = {}
        for start_node, end_node, _ in airport_graph.edges(data=True):
            
            # set default color and transparency
            edge_color = other_edge_color
            edge_alpha = 0.05
            
            # set booleans for whether current edge is selected edge
            from_cond = (airport_graph.nodes[start_node]["iata_code"] == from_iata) or (airport_graph.nodes[end_node]["iata_code"] == from_iata)
            to_cond = (airport_graph.nodes[start_node]["iata_code"] == to_iata) or (airport_graph.nodes[end_node]["iata_code"] == to_iata)
            
            # update color and transparency only for selected edge
            if from_cond and to_cond:
                edge_color = selected_edge_color
                edge_alpha = 1
            
            # update edge attribute dictionary
            edge_attr[(start_node, end_node)] = {"edge_color": edge_color,
                                                 "edge_alpha": edge_alpha}
        
        # update graph edge attributes
        nx.set_edge_attributes(airport_graph, edge_attr)
        # update bokeh plot with new networkx graph
        network = from_networkx(airport_graph, pos)
        # create node renderer
        network.node_renderer.glyph = Scatter(size=15, fill_color="cornflowerblue")
        # create edge renderer
        network.edge_renderer.glyph = MultiLine(line_color="edge_color", line_alpha="edge_alpha", line_width=2)
        # append new renderer or replace previous renderer
        if len(network_plot.renderers) == 0:
            network_plot.renderers.append(network)
        else: 
            network_plot.renderers[0] = network
    
    # if no data are encountered for selected airports, report no data 
    n = selection_data.shape[0]
    if n == 0:
        for i in range(len(summary_data["stat_values"])):
            summary_data["stat_values"][i] = "No flight data available"
        sum_source.data = summary_data
        
        ovr_source.data = dict(
            top_locs = [],
            left_locs = [],
            right_locs = []
            )
        pct_source.data = dict(
                labels = pct_labels,
                top_locs = [0]*len(pct_labels)
            )
        
    # if data available, update drilldown graphics
    else:
        # update summary data
        d_stats = selection_data["OVERALL_DELAY"].describe()
        summary_data["stat_values"][0] = int(d_stats["count"])
        avg_delay = round((d_stats["mean"]), 2)
        std_delay = round(d_stats["std"], 2)
        if avg_delay < 0:
            summary_data["stat_values"][1] = "Early by {} minutes".format(-avg_delay)
        else:
            summary_data["stat_values"][1] = "Late by {} minutes".format(avg_delay)
        
        
        # use random forest to predict delays on route
        X = selection_data[feature_cols]
        preds = rf_model.predict(X)
        
        # calculate high, low, and average delay prediction
        min_pred = round(np.min(preds), 2)
        avg_pred = round(np.mean(preds), 2)
        max_pred = round(np.max(preds), 2)
        
        # report high, low, and average delay prediction in bokeh table
        if min_pred < 0:
            summary_data["stat_values"][2] = "Early by {} minutes".format(-min_pred)
        else:
            summary_data["stat_values"][2] = "Late by {} minutes".format(min_pred)
        
        if avg_pred < 0:
            summary_data["stat_values"][3] = "Early by {} minutes".format(-avg_pred)
        else:
            summary_data["stat_values"][3] = "Late by {} minutes".format(avg_pred)
        
        if max_pred < 0:
            summary_data["stat_values"][4] = "Early by {} minutes".format(-max_pred)
        else:
            summary_data["stat_values"][4] = "Late by {} minutes".format(max_pred)
        
        # report score
        summary_data["stat_values"][5] = route_score(avg_delay, std_delay, int(d_stats["count"]))
        sum_source.data = summary_data
        
        
        # update overall delay data
        ovr_hist, ovr_edges = np.histogram(selection_data["OVERALL_DELAY"].dropna())
        ovr_source.data = dict(
            top_locs = ovr_hist,
            left_locs = ovr_edges[:-1],
            right_locs = ovr_edges[1:]
            )
        
        # update percent delayed and cancelled
        dep_delays = selection_data[selection_data["DEP_DELAY"] > 0].shape[0]
        arr_delays = selection_data[selection_data["ARR_DELAY"] > 0].shape[0]
    
        dep_delay_pct = dep_delays/n*100
        arr_delay_pct = arr_delays/n*100
    
        pct_heights = [dep_delay_pct, arr_delay_pct]
        pct_source.data = dict(
                labels = pct_labels,
                top_locs = pct_heights
            )     

# link select tools to update function
controls = [month_select, day_select, airline_select, from_select, to_select]
for control in controls:
    control.on_change("value", lambda attr, old, new: update())

# create layout
dash_layout = layout(
    [
        [month_select, day_select, airline_select, from_select, to_select],
        [
            network_plot,
            [
                [data_table], [ovr_plot], [pct_plot],
            ]
        ]
    ],
    sizing_mode="fixed")

# initialize data based on default parameters
update()

# add layout to current document
curdoc().add_root(dash_layout)
