# fix direct reference to mini shifts
def getOnIceFor(row):
    time = row["eventTime"]
    for_id = row["team_id_for"]
    on_ice_for = mini_shifts[(mini_shifts["shift_start"] < time) & (mini_shifts["shift_end"] >= time) & (mini_shifts["team_id"] == for_id)]
    on_ice_for_ids = on_ice_for["player_id"].to_list()
    return on_ice_for_ids

import pandas as pd

path = "../hockey_data/"
plays = pd.read_csv(path + 'game_plays.csv')
plays = plays.drop_duplicates()
plays = plays.drop(columns = ["secondaryType", "x", "y", "periodTimeRemaining", "st_x", "st_y"])
plays = plays[plays["periodType"] != "SHOOTOUT"]
plays["eventTime"] = plays.apply(lambda x: x["periodTime"] + 1200 * (x["period"]-1), axis = 1)
goals = plays[plays["event"] == "Goal"]

shifts = pd.read_csv(path + "game_shifts.csv")
shifts = shifts.drop_duplicates()

games = pd.read_csv(path + "game.csv")
games = games.drop_duplicates()

players = pd.read_csv(path + "player_info.csv")
players = players.drop_duplicates()
skaters = players[players["primaryPosition"] != "G"]

player_team = pd.read_csv(path + "game_skater_stats.csv")
player_team = player_team.drop_duplicates()
player_team = player_team[["game_id", "player_id", "team_id"]]

### Single Game ###
game_id = 2014020700
mini_plays = plays[plays["game_id"] == game_id]

mini_plays["eventTime"] = mini_plays.apply(lambda x: x["periodTime"] + 1200 * (x["period"]-1), axis = 1)
mini_plays = mini_plays.sort_values(by = "eventTime")
mini_plays = mini_plays[mini_plays["event"] == "Goal"]

mini_shifts = shifts[shifts["game_id"] == game_id]
mini_shifts = mini_shifts.sort_values(by = "shift_start")

mini_pp = player_team[player_team["game_id"] == game_id]
mini_shifts = mini_shifts.merge(mini_pp[["player_id", "team_id"]], on = "player_id", how = "left")
mini_shifts = mini_shifts.merge(players[["player_id", "firstName", "lastName"]], on = "player_id", how = "left")

mini_plays["on_ice_for"] = mini_plays.apply(getOnIceFor, axis = 1)
mini_plays.iloc[0]["on_ice_for"]
####################

### Single Season ###
season = 20142015
mini_games = games[games["season"] == season]
game_ids = mini_games["game_id"].unique()
season_goals = goals[goals["game_id"].isin(game_ids)]
all_games = []
for game_id in game_ids:
    mini_goals = season_goals[season_goals["game_id"] == game_id]
    mini_shifts = shifts[shifts["game_id"] == game_id]
    
    mini_player_info = player_team[player_team["game_id"] == game_id]
    mini_shifts = mini_shifts.merge(mini_player_info[["player_id", "team_id"]], on = "player_id", how = "left")
    mini_shifts = mini_shifts.merge(players[["player_id", "firstName", "lastName"]], on = "player_id", how = "left")
    
    mini_goals["on_ice_for"] = mini_goals.apply(getOnIceFor, axis = 1)
    all_games.append(mini_goals)
new_season_goals = pd.concat(all_games)
# export to csv
new_season_goals.to_csv(path + "goals1415.csv", index = False)
####################




# extra degree for scorer?
# extra degree on node or weight on edge for assister and scorer?
# time dist of scoring (e.g. histogram of scoring by minute)?
