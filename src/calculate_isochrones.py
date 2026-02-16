import os
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from shapely.geometry import LineString, Point, Polygon

from pyproj import Transformer 

import pandas as pd
import numpy as np

# settings, default constants

SOURCE_CRS = "epsg:4326"
TARGET_CRS = "epsg:31287"

PLACES = [{"city": "Vienna", "country": "Austria"},
          {"state": "Lower Austria", "country": "Austria"},
          {"state": "Upper Austria", "country": "Austria"},
          {"state": "Burgenland", "country": "Austria"},
          {"state": "Salzburg", "country": "Austria"},
          {"state": "Styria", "country": "Austria"},
          {"state": "Carinthia", "country": "Austria"},
          {"state": "Tyrol", "country": "Austria"},
          {"state": "Vorarlberg", "country": "Austria"}]

NETWORK_TYPE = "walk"

DISTANCES = [300, 500, 750, 1000, 1250]
PTSQL_COLORS = ["#E42421", "#E95153", "#E63C1E", "#F29668", "#34672B", "#87C281", "#959595", "none"]

# input data
PATH_GRAPHS_IN = "../data/in/osmnx_graphs/"
PATH_STOPS_IN = "../data/out/stop_dfs/"

# output data
PATH_ISOCHRONES_OUT = "../data/out/isochrones_gpkg/"
PATH_FIGS_OUT = "../data/out/figs/"


PTSQL_COLOR_TABLE = [[0,0,1,2,3], # I
                    [0,1,2,3,4], # II
                    [1,2,3,4,5], # III
                    [2,3,4,5,6], # IV
                    [3,4,5,6,6], # V
                    [4,5,6,-1,-1], # VI
                    [5,6,6,-1,-1], # VII
                    [6,6,-1,-1,-1]] # VIII


def assign_color(category, distance):
    """
    Lookup the ptsql based on the station category and the distance level.
    """
    if distance <= 300:
        return PTSQL_COLOR_TABLE[category][0]
    elif distance <= 500:
        return PTSQL_COLOR_TABLE[category][1]
    elif distance <= 750:
        return PTSQL_COLOR_TABLE[category][2]
    elif distance <= 1000:
        return PTSQL_COLOR_TABLE[category][3]
    elif distance <= 1250:
        return PTSQL_COLOR_TABLE[category][4]
    else:
        return -1
    
def draw_graph(G, ns=0, nc="none", gdf=None, return_fig=False):
    """
    Draw the graph with the specified node sizes and node colors.
    Optionally add a geodataframe to the plot if provided.
    
    Parameters:
        G (nx.Graph): The graph to draw.
        ns (int): The node size.
        nc (str): The node color.
        gdf (gpd.GeoDataFrame): The geodataframe containing the nodes.
        return_fig (bool): If True, return the figure and axis.

    Returns:
        fig, ax (tuple): The figure and axis if return_fig is True.
    """
    fig, ax = ox.plot.plot_graph(
        G,
        node_color=nc,
        node_size=ns,
        edge_color="#999999",
        edge_alpha=0.2,
        show=False,
        close=False,
        figsize=(12, 12),
        dpi=300,
    )
    if gdf is not None:
        gdf.plot(ax=ax, color=gdf.index, ec="none", alpha=1, zorder=-1)

    #plt.show()

    if return_fig:
        return fig, ax
    

def load_graph(places: list[dict], network_type: str = NETWORK_TYPE, union: bool = False, crs: str = TARGET_CRS) -> list[nx.Graph] | nx.Graph:
    """
    Load the graph of the specified places from the data folder.
    Or download the graph from OSM if it does not exist.

    Parameters:
        places (list[dict]): A list of dictionaries containing the place information.
        network_type (str): The network type to use for the graph. Defaults to "walk".
        union (bool): If True, union the graphs of the places. Defaults to False.

    Returns:
        list[nx.Graph] or nx.Graph: A list of graphs if union is False, otherwise a single graph.
    """

    #data_path = "../data/in/osmnx_graphs/"
    #ox.save_graphml(G, f"{data_path}/graph_{place.split(',')[0]}.graphml")
    #ox.save_graphml(G, f"{data_path}/graph_{place["state"]}.graphml")

    graphs = []

    for place in places:
        name = place.get("state", place.get("city"))

        if os.path.exists(f"{PATH_GRAPHS_IN}/graph_{name}.graphml"):
            G = ox.load_graphml(f"{PATH_GRAPHS_IN}/graph_{name}.graphml")
        else:
            G = ox.graph_from_place(place, network_type=network_type)
            ox.save_graphml(G, f"{PATH_GRAPHS_IN}/graph_{name}.graphml")

        G = ox.projection.project_graph(G, to_crs=crs)
        graphs.append(G)

    if union:
        return nx.union_all(graphs)

    return graphs

def load_stops(regions: list[str] = ["all_regions"], day: int = 20240528, crs: str = TARGET_CRS) -> pd.DataFrame:
    """
    Load the stops of the specified places and day from the data folder.

    Parameters:
        places (list[str]): A list of places to load the stops for. Defaults to ["all_regions"].
        day (int): The day to load the stops for. Defaults to 20240528.
        crs (str): The CRS to project the stops to. Defaults to target_crs.

    Returns:
        pd.DataFrame: A DataFrame containing the stops for the specified places and day.
    """

    dfs = []
    for region in regions:
        dfs.append(pd.read_csv(f"{PATH_STOPS_IN}{region}_{day}.csv"))

    df = pd.concat(dfs)

    transformer = Transformer.from_crs(SOURCE_CRS, crs, always_xy=True)
    df["x"], df["y"] = transformer.transform(df["stop_lon"].values, df["stop_lat"].values)

    return df


def calculate_isochrones(G, stops, distances=DISTANCES, crs=TARGET_CRS, buffer=1) -> gpd.GeoDataFrame:
    """
    Calculate the isochrones for the specified distances.
    
    Parameters:
        G (nx.Graph): The graph to calculate the isochrones for.
        stops (pd.DataFrame): The stops to calculate the isochrones for.
        distances (list[int]): A list of distances in meters. Defaults to DISTANCES.
        crs (str): The CRS to project the isochrones to. Defaults to target_crs.
        buffer (int): The buffer size in meters. Smooths the isochrones. Defaults to 1.
    
    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the isochrones for each stop and distance.
    """
    # for each stop select the closes node in the graph to represent it
    nodes, dists = ox.nearest_nodes(G, stops['x'], stops['y'], return_dist=True)

    # TODO: some nodes in the graph are far away (> 50m) from the actual stop location. Do we need to filter them out???

    #create list node_id, stop_id, category
    node_list = np.rec.fromarrays([nodes, stops["stop_id"], stops['category']])

    # print(node_list)
    # print(len(node_list))

    distances.sort()

    records = []

    for cn,_,cat in node_list:

        # select all nodes within the max distance
        lengths = nx.single_source_dijkstra_path_length(
            G,
            cn,
            cutoff=distances[-1],
            weight="length"
        )

        prev_d = 0
        # for each distance, select all nodes in the distance band
        for d in distances:
            ring_nodes = [ Point((G.nodes[n]["x"], G.nodes[n]["y"])) for n, dist in lengths.items() if prev_d < dist <= d ]

            if ring_nodes:
                poly = gpd.GeoSeries(ring_nodes).union_all().convex_hull.buffer(1)
                records.append({
                    "center": cn,
                    "distance": d,
                    "color": PTSQL_COLORS[assign_color(cat, d)],
                    "geometry": poly
                })

            prev_d = d

    gdf = gpd.GeoDataFrame(records, crs=crs)

    # dissolve polygons of same color into one shape (Multipolygon) and reorder by reversed PTSQL_COLORS (largest shape first)
    # this allows plotting the polygons in the correct order to make smaller polygons on top of larger ones
    gdf = gdf.dissolve(by="color").reindex(PTSQL_COLORS[::-1])

    return gdf
 

if __name__ == "__main__":
    day = 20240528
    place = {"city": "Bregenz", "country": "Austria"}
    region = "vmobil_obb"

    stops = load_stops([region], day)
    G = load_graph([place])

    G = G[0] if len(G) == 1 else G

    isochrones = calculate_isochrones(G, stops)

    print(isochrones)

    # draw
    fig, ax = draw_graph(G, gdf=isochrones, return_fig=True)

    name = f"{place.get('state', place.get('city'))}_{day}"

    isochrones.to_file(f"{PATH_ISOCHRONES_OUT}{name}.gpkg", layer="isochrones", driver="GPKG")
    fig.savefig(f"{PATH_FIGS_OUT}{name}.png")

    plt.figure(fig)
    plt.show()
