import pandas as pd
import datetime
data_path = "../airline_data/2019data.csv"
lookup_path = "../airline_data/carrier_lookup.csv"

data = pd.read_csv(data_path)
data = data.dropna()

carriers = pd.read_csv(lookup_path)

top_30_airports_iata = ["ATL", "DFW", "DEN", "ORD", "LAX",
                        "JFK", "LAS", "MCO", "MIA", "CLT",
                        "SEA", "PHX", "EWR", "SFO", "IAH",
                        "BOS", "FLL", "MSP", "LGA", "DTW",
                        "PHL", "SLC", "DCA", "SAN", "BWI",
                        "TPA", "AUS", "IAD", "BNA", "MDW"]
top_count = 30
top_airports = top_30_airports_iata[:top_count]
data = data[data["ORIGIN"].isin(top_airports) & data["DEST"].isin(top_airports)]

data.loc[:, "OVERALL_DELAY"] = data.apply(lambda x: x["ACTUAL_ELAPSED_TIME"] - x["CRS_ELAPSED_TIME"], axis = 1)

seasons = ["Winter", "Spring", "Summer", "Fall"]

def date_to_season(current_timestamp):
    date = current_timestamp.split()[0]
    month, day, year = date.split("/")
    current_datetime = datetime.date(int(year), int(month), int(day))
    ref_dates = [ 
        datetime.date(int(year), 3, 21),
        datetime.date(int(year), 6, 21),
        datetime.date(int(year), 9, 21),
        datetime.date(int(year), 12, 21)
        ]
    if (current_datetime < ref_dates[0]):
        return "Winter"
    elif (current_datetime < ref_dates[1]):
        return "Spring"
    elif (current_datetime < ref_dates[2]):
        return "Summer"
    elif (current_datetime < ref_dates[3]):
        return "Fall"
    else:
        return "Winter"

data.loc[:, "SEASON"] = data.apply(lambda x: date_to_season(x["FL_DATE"]), axis = 1)

for season in seasons:
    data.loc[:, season] = data.apply(lambda x: 1 if x["SEASON"] == season else 0, axis = 1)

data = data.merge(carriers, left_on = "MKT_UNIQUE_CARRIER", right_on = "Code", how = "inner")

data.loc[:, "AIRLINE"] = data.apply(lambda x: x["Description"].split()[0], axis = 1)

airlines = sorted(list(data["AIRLINE"].unique()))

for airline in airlines:
    data.loc[:, "AIRLINE" + airline] = data.apply(lambda x: 1 if x["AIRLINE"] == airline else 0, axis = 1)

keep = ["MONTH", "DAY_OF_MONTH", "SEASON", "AIRLINE",
        "ORIGIN_AIRPORT_ID", "ORIGIN", "DEST_AIRPORT_ID", "DEST", 
        "DEP_DELAY", "ARR_DELAY", "CANCELLED", "CRS_ELAPSED_TIME", 
        "ACTUAL_ELAPSED_TIME", "OVERALL_DELAY"]
keep += ["AIRLINE" + airline for airline in airlines]
keep += seasons
data = data[keep]

data.to_csv("2019top30data2.csv", index=False)
data.to_parquet("2019top30data2.parquet", compression=None)
