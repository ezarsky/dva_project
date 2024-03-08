
import pandas as pd
import csv

path = "../hockey_data/"
goals = pd.read_csv(path + "goals1415.csv")

player_groups = goals["on_ice_for"].to_list()
group_list = [group.strip("[]").split(",") for group in player_groups]
    
edges = []
nodes = {}
for group in group_list:
    n = len(group)
    for i, player in enumerate(group):
        if player != "":
            nodes[player] = nodes.get(player, 0) + n-1
        for j in range(i+1, n):
            edge1 = (group[i], group[j])
            edge2 = (group[j], group[i])
            if not ((edge1 in edges) or (edge2 in edges)):
                edges.append(edge1)

nodes_file = open(path + "nodes1415.csv", "w", encoding="utf-8")
nodes_file.write("id,degree"+"\n")
for node, degree in nodes.items():
    nodes_file.write(node + "," + str(degree) + "\n")
nodes_file.close()

edges_file = open(path + "edges1415.csv", "w", encoding="utf-8")
edges_file.write("source,target" + "\n")
for edge in edges:
    edges_file.write(edge[0] + "," + edge[1] + "\n")
edges_file.close()
