import pandas as pd
import numpy as np
import networkx as nx
from bokeh.plotting import figure, from_networkx, show
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, MultiLine, Range1d, Scatter, Select

# uncomment to work in jupyter notebook, use "show" to see results
#from bokeh.io import output_notebook
#output_notebook()

###################
### Data Import ###
###################
# import data and lookup table for airport codes
data_path = "../airline_data/2019_06.csv"
lookup_path = "../airline_data/airport_lookup.csv"

data = pd.read_csv(data_path)
keep = ["MONTH", "DAY_OF_MONTH", "DAY_OF_WEEK", "FL_DATE", "MKT_UNIQUE_CARRIER",
        "ORIGIN_AIRPORT_ID", "ORIGIN", "DEST_AIRPORT_ID", "DEST", "CRS_DEP_TIME",
        "DEP_TIME", "DEP_DELAY", "TAXI_OUT", "WHEELS_OFF", "WHEELS_ON", "TAXI_IN",
        "CRS_ARR_TIME", "ARR_TIME", "ARR_DELAY", "CANCELLED", "CANCELLATION_CODE",
        "DIVERTED", "DUP", "CRS_ELAPSED_TIME", "ACTUAL_ELAPSED_TIME", "AIR_TIME", 
        "DISTANCE", "CARRIER_DELAY", "WEATHER_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]

data = data[keep]

code_lookup = pd.read_csv(lookup_path)



#####################
### Data Cleaning ###
#####################
top_30_airports_iata = ["ATL", "DFW", "DEN", "ORD", "LAX",
                        "JFK", "LAS", "MCO", "MIA", "CLT",
                        "SEA", "PHX", "EWR", "SFO", "IAH",
                        "BOS", "FLL", "MSP", "LGA", "DTW",
                        "PHL", "SLC", "DCA", "SAN", "BWI",
                        "TPA", "AUS", "IAD", "BNA", "MDW"]
top_count = 7
top_airports = top_30_airports_iata[:top_count]
data = data[data["ORIGIN"].isin(top_airports) & data["DEST"].isin(top_airports)]
code_lookup = code_lookup[code_lookup["code_iata"].isin(top_airports)]
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
    from_mask = code_lookup["code_dot"] == pair[0]
    from_row = code_lookup[from_mask]
    from_node = {
        "name": from_row["airport_name"].values[0],
        "iata_code": from_row["code_iata"].values[0],
        "geo_coords": (from_row["latitude"].values[0], 
                       from_row["longitude"].values[0]),
        "flight_count": flight_counts[pair[0]]
    }


    to_mask = code_lookup["code_dot"] == pair[1]
    to_row = code_lookup[to_mask]
    to_node = {
        "name": to_row["airport_name"].values[0],
        "iata_code": to_row["code_iata"].values[0],
        "geo_coords": (to_row["latitude"].values[0], 
                       to_row["longitude"].values[0]),
        "flight_count": flight_counts[pair[1]]
    }
    from_option = from_node["name"] + " (" + from_node["iata_code"] + ")"
    to_option = to_node["name"] + " (" + to_node["iata_code"] + ")"
    if not from_node in airports:
        airports.append(from_node)
    if not to_node in airports:
        airports.append(to_node)
    flight_pairs.append((from_node, to_node))
    from_airports.append(from_option)
    to_airports.append(to_option)

from_airports = sorted(list(set(from_airports)))
to_airports = sorted(list(set(to_airports)))

from_iata = from_airports[0][-4:-1]
to_iata = from_airports[1][-4:-1]

################
### Modeling ###
################




#####################
### Network Graph ###
#####################
#specify colors
bgcolor = "ghostwhite"
ddcolor = "midnightblue"
selected_edge_color = "#333333"
other_edge_color = "#dddddd"
# TODO: incorporate modeling and metrics in node and edge info
# create Graph
airport_graph = nx.Graph()
for airport in airports:
    airport_graph.add_node(airport["iata_code"], 
                           pos=(airport["geo_coords"][1],
                                airport["geo_coords"][0]))

for pair in flight_pairs:
    airport_graph.add_edge(pair[0]["iata_code"], pair[1]["iata_code"])

airport_graph = nx.convert_node_labels_to_integers(airport_graph, label_attribute="iata_code")


edge_attr = {}
for start_node, end_node, _ in airport_graph.edges(data=True):
    edge_color = other_edge_color
    from_cond = (airport_graph.nodes[start_node]["iata_code"] == from_iata) or (airport_graph.nodes[end_node]["iata_code"] == from_iata)
    to_cond = (airport_graph.nodes[start_node]["iata_code"] == to_iata) or (airport_graph.nodes[end_node]["iata_code"] == to_iata)
    if from_cond and to_cond:
        edge_color = selected_edge_color
    edge_attr[(start_node, end_node)] = edge_color

nx.set_edge_attributes(airport_graph, edge_attr, "edge_color")

pos = nx.get_node_attributes(airport_graph, 'pos')
#nx.draw(airport_graph, pos, with_labels=True)

##########################
### Interactive Visual ###
##########################
# plot and widget size parameters
figure_width = 800
network_w = int(0.75*figure_width)
network_h = network_w

drilldown_count = 2
w = int(0.35*figure_width)
h = int(network_h/drilldown_count)


# create interactive selectors in bokeh
widget_count = 2
widget_width = int(figure_width/widget_count)
from_select = Select(title="Where from?", options=from_airports, 
                     value=from_airports[0], width=widget_width)
to_select = Select(title="Where to?", options=to_airports, 
                   value=from_airports[1], width=widget_width)

# create labels for plots and data filtering
pct_labels = ["Departure Delay", "Arrival Delay", "Cancelled"]
#delay_types = ["CARRIER_DELAY", "WEATHER_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY"]
#type_plot_labels = ["Car", "Wth", "Sec", "Late"]

# create ColumnDataSources for each plot 

pct_source = ColumnDataSource(data = dict(
        labels = [],
        top_locs = []
    ))

ovr_source = ColumnDataSource(data = dict(
        top_locs = [],
        left_locs = [],
        right_locs = []
    ))

##################
### Plot Setup ###
##################
# initialize network plot
network_plot = figure(width = network_w, height = network_h, sizing_mode="fixed", 
                      x_axis_location=None, y_axis_location=None, toolbar_location=None,
                      title="Airport Network", background_fill_color=bgcolor)
network_plot.grid.grid_line_color = None

# TODO: initialize summary data table plot

# initialize overall delays plot
ovr_plot = figure(width = w, height = h, sizing_mode="fixed", 
                  toolbar_location=None, title="Delay Lengths (minutes)",
                  background_fill_color=bgcolor)
ovr_plot.quad(top="top_locs", bottom=0, left="left_locs", right="right_locs",
              source=ovr_source, fill_color=ddcolor, line_color="white")
ovr_plot.y_range.start=0
ovr_plot.xaxis.axis_label = "Delay time (minutes)"
ovr_plot.yaxis.axis_label = "Frequency"

# initialize percentage delayed/cancelled plot
pct_plot = figure(width = w, height = h, sizing_mode="fixed",
                  x_range=pct_labels, y_range=Range1d(0, 100),
                  toolbar_location=None, title="Percent Delayed/Cancelled",
                  background_fill_color=bgcolor)
pct_plot.vbar(x="labels", top="top_locs", source = pct_source, 
              fill_color=ddcolor, line_color="white", width = 0.8)
pct_plot.xaxis.axis_label = "Delay/Cancellation"
pct_plot.yaxis.axis_label = "% of flights on route delayed/cancelled"


# function for filtering data to only selected origin and destination

def select_flights():
    from_iata = from_select.value[-4:-1]
    to_iata = to_select.value[-4:-1]
    from_dot = int(code_lookup.loc[code_lookup["code_iata"] == from_iata, "code_dot"].values[0])
    to_dot = int(code_lookup.loc[code_lookup["code_iata"] == to_iata, "code_dot"].values[0])
    # handle case of same origin and destination (no update)
    if from_dot != to_dot:
        selection_data = data.loc[flight_pairs_dict[(from_dot, to_dot)]]
        return selection_data

# function for updating data sources based on selections
def update():
    from_iata = from_select.value[-4:-1]
    to_iata = to_select.value[-4:-1]
    # handle case of same origin and destination (no update)
    if from_iata != to_iata:
        selection_data = select_flights()
        n = selection_data.shape[0]
        
        
        # update network graph
        edge_attr = {}
        for start_node, end_node, _ in airport_graph.edges(data=True):
            edge_color = other_edge_color
            from_cond = (airport_graph.nodes[start_node]["iata_code"] == from_iata) or (airport_graph.nodes[end_node]["iata_code"] == from_iata)
            to_cond = (airport_graph.nodes[start_node]["iata_code"] == to_iata) or (airport_graph.nodes[end_node]["iata_code"] == to_iata)
            if from_cond and to_cond:
                edge_color = selected_edge_color
            edge_attr[(start_node, end_node)] = edge_color
        
        nx.set_edge_attributes(airport_graph, edge_attr, "edge_color")
        network = from_networkx(airport_graph, pos)
        network.node_renderer.glyph = Scatter(size=15, fill_color="cornflowerblue")
        network.edge_renderer.glyph = MultiLine(line_color="edge_color", line_alpha=1, line_width=2)
        network_plot.renderers.append(network)
    
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
        

# link select tools to update function
controls = [from_select, to_select]
for control in controls:
    control.on_change("value", lambda attr, old, new: update())

# create layout
dash_layout = layout(
    [
        [from_select, to_select],
        [
            network_plot,
            [
                [ovr_plot], [pct_plot],
            ]
        ]
    ],
    sizing_mode="fixed")

# initialize data based on default parameters
update()

# add layout to current document
curdoc().add_root(dash_layout)

