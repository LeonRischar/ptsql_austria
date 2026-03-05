from functools import partial
import math
import os
import pickle
import time
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from shapely.geometry import LineString, Point

from pyproj import Transformer 

import pandas as pd
import numpy as np

from multiprocessing import Pool, TimeoutError
from itertools import repeat

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
    
def create_name(place):
    """
    Create a name for the graph and output files. Also used to find existing graphs.

    Parameters:
        place (dict | list[dict]): The place to create the name for.

    Returns:    
        str: The name for the graph and output files.
    """

    name = ""
    if place == PLACES:
        name = "all_regions"
    elif isinstance(place, list):
        name = "_".join([p.get('state', p.get('city', "")) for p in place])
    else:
        name += place.get('state', place.get('city', ""))

    return name
    
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
    

def load_graph(places: list[dict] | dict, network_type: str = NETWORK_TYPE, union: bool = True, crs: str = TARGET_CRS, save: bool = True) -> list[nx.Graph] | nx.Graph:
    """
    Load the graph of the specified places from the data folder.
    Or download the graph from OSM if it does not exist.

    Parameters:
        places (list[dict]): A list of dictionaries containing the place information.
        network_type (str): The network type to use for the graph. Defaults to "walk".
        union (bool): If True, combine the graphs of the places to one graph. Defaults to True.
        crs (str): The CRS to project the graph to. Defaults to TARGET_CRS.
        save (bool): If True, save the graph(s) to the data folder. Defaults to True.

    Returns:
        list[nx.Graph] or nx.Graph: A list of graphs if union is False, otherwise a single graph.
    """

    graphs = []

    if not isinstance(places, list):
        places = [places]

    for place in places:
        n = place.get("state", place.get("city", ""))

        if os.path.exists(f"{PATH_GRAPHS_IN}graph_{n}.pkl"):
            #G = ox.load_graphml(f"{PATH_GRAPHS_IN}/graph_{n}.graphml")
            print(f"Loading existing graph for {n}" + ' '*20, end="\r")
            with open(f"{PATH_GRAPHS_IN}graph_{n}.pkl", "rb") as f:
                g = pickle.load(f)
        else:
            print(f"Downloading graph for {n}" + ' '*20, end="\r")
            g = ox.graph_from_place(place, network_type=network_type)
            #ox.save_graphml(G, f"{PATH_GRAPHS_IN}/graph_{n}.graphml")
            if save:
                with open(f"{PATH_GRAPHS_IN}graph_{n}.pkl", "wb") as f:
                    pickle.dump(g, f, protocol=pickle.HIGHEST_PROTOCOL)

        graphs.append(g)

    if union:
        #print(f"Combining graphs" + ' '*20, end="\r")
        #time_before = time.time()
        g = nx.compose_all(graphs)
        #time_after = time.time()
        #print(f"Combined graphs in {time_after - time_before:.3f}s" + ' '*20)

        # NOTE: most time spent on projection
        g = ox.projection.project_graph(g, to_crs=crs)
        return g
    
    if len(graphs) == 1:
        return ox.projection.project_graph(graphs[0], to_crs=crs)
    else:
        return [ox.projection.project_graph(g, to_crs=crs) for g in graphs]


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
    df.drop_duplicates(subset=["stop_id"], inplace=True)

    transformer = Transformer.from_crs(SOURCE_CRS, crs, always_xy=True)
    df["x"], df["y"] = transformer.transform(df["stop_lon"].values, df["stop_lat"].values)

    return df


def calculate_isochrones(G, stops, distances=DISTANCES, crs=TARGET_CRS, buffer=25, nearest_node_threshold=50, edge_snapping=False) -> gpd.GeoDataFrame:
    """
    Calculate the isochrones for the specified distances.
    
    Parameters:
        G (nx.Graph): The graph to calculate the isochrones for.
        stops (pd.DataFrame): The stops to calculate the isochrones for.
        distances (list[int]): A list of distances in meters. Defaults to DISTANCES.
        crs (str): The CRS to project the isochrones to. Defaults to target_crs.
        buffer (int): The buffer size in meters. Smooths the isochrones. Defaults to 1.
        nearest_node_threshold (int): The maximum distance in meters to consider a node as a stop. Otherwise use edge snapping. Defaults to 50.
        edge_snapping (bool): If True, use edge snapping for all stops. Other wise use edge snapping only futher away than nearest_node_threshold. Defaults to False.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing the isochrones for each stop and distance.
    """

    if edge_snapping:
        # calculate isochrones with edge snapping for all stops
        gdf = calculate_isochrones_nearest_edges(G, stops, distances, crs, buffer)
        return gdf

    # for each stop select the closes node in the graph to represent it
    nodes, dists = ox.nearest_nodes(G, stops['x'], stops['y'], return_dist=True)

    # select stop nodes furter away than 50m from actual stop location
    far_away_ids = np.where(dists > nearest_node_threshold)[0]
    stops_far_away = stops.iloc[far_away_ids]
    # calculate isochrones with edge snapping for far away stops
    gdf_snapping = calculate_isochrones_nearest_edges(G, stops_far_away, distances, crs, buffer)

    #create list node_id, stop_id, category
    node_list = np.rec.fromarrays([nodes, stops["stop_id"], stops['category']])
    # remove far away stops from nodes list
    node_list = np.delete(node_list, far_away_ids)

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
            color = PTSQL_COLORS[assign_color(cat, d)]
            if color == "none": #skip black areas
                break #skip entire loop for this node since there are no colored isos left

            ring_nodes = [ Point((G.nodes[n]["x"], G.nodes[n]["y"])) for n, dist in lengths.items() if prev_d < dist <= d ]

            if ring_nodes:
                poly = gpd.GeoSeries(ring_nodes).union_all().convex_hull.buffer(buffer)

                records.append({
                    "center": cn,
                    "distance": d,
                    "color": color,
                    "geometry": poly
                })

            prev_d = d

    gdf = gpd.GeoDataFrame(records, crs=crs)
    # add snapping gdf to main gdf
    gdf = gpd.GeoDataFrame(pd.concat([gdf, gdf_snapping]))

    # dissolve polygons of same color into one shape (Multipolygon) and reorder by reversed PTSQL_COLORS (largest shape first)
    # this allows plotting the polygons in the correct order to make smaller polygons on top of larger ones
    gdf = gdf.dissolve(by="color").reindex(PTSQL_COLORS[::-1])

    return gdf
 
def calculate_isochrones_nearest_edges(G, stops, distances=DISTANCES, crs=TARGET_CRS, buffer=25) -> gpd.GeoDataFrame:
    """
    Same as calculate_isochrones but uses nearest_edges and node snapping instead of nearest_nodes
    """
    edges, dists = ox.nearest_edges(G, stops['x'], stops['y'], return_dist=True)
    edge_list = np.rec.fromarrays([edges, stops["stop_id"], stops['category'], stops['x'], stops['y']])

    distances.sort()

    records = []

    for e,_,cat,x,y in edge_list:

        # prepare vars
        u,v,k = e
        edge = G.get_edge_data(u, v, k)
        # some edges have no geometry attribute, so add straight line as default
        geom = edge.get("geometry", LineString([(G.nodes[u]["x"], G.nodes[u]["y"]),(G.nodes[v]["x"], G.nodes[v]["y"]),]))
            
        p = Point(x, y)

        # project point to nearest edge
        proj_dist = geom.project(p)
        snap_point = geom.interpolate(proj_dist)

        # calculate the distance of snapped point to each edge endpoint, turn both end nodes into points
        dist_to_u = snap_point.distance(Point(G.nodes[u]["x"], G.nodes[u]["y"]))
        dist_to_v = snap_point.distance(Point(G.nodes[v]["x"], G.nodes[v]["y"]))

        # run dijkstra to get reachable node for each edge endpoint with adjusted max distance
        lengths_u = nx.single_source_dijkstra_path_length(
            G,
            u,
            cutoff=distances[-1]-dist_to_u,
            weight="length"
        )
        lengths_v = nx.single_source_dijkstra_path_length(
            G,
            v,
            cutoff=distances[-1]-dist_to_v,
            weight="length"
        )

        # add back distance to each reachable node
        lengths_u = {n: d + dist_to_u for n, d in lengths_u.items()}
        lengths_v = {n: d + dist_to_v for n, d in lengths_v.items()}

        # merge node sets and keep shorter distance if exists in both sets
        lengths = {
            n: min(lengths_u.get(n, np.inf), lengths_v.get(n, np.inf)) for n in lengths_u.keys() | lengths_v.keys()
        }

        # do isochrone calculation as before
        
        prev_d = 0
        # for each distance, select all nodes in the distance band
        for d in distances:
            color = PTSQL_COLORS[assign_color(cat, d)]
            if color == "none": #skip black areas
                break #skip entire loop for this node since there are no colored isos left

            ring_nodes = [ Point((G.nodes[n]["x"], G.nodes[n]["y"])) for n, dist in lengths.items() if prev_d < dist <= d ]

            if ring_nodes:
                poly = gpd.GeoSeries(ring_nodes).union_all().convex_hull.buffer(buffer)
                records.append({
                    "center": snap_point,
                    "distance": d,
                    "color": color,
                    "geometry": poly
                })

            prev_d = d
    
    gdf = gpd.GeoDataFrame(records, crs=G.graph["crs"])
    gdf = gdf.dissolve(by="color").reindex(PTSQL_COLORS[::-1])

    return gdf

def calculate_batch_isochrones(places, regions, days, edge_snapping=False):
    """
    Calculate the isochrones for all the specified places and regions each day seprately in parallel.
    Can also be used for a single day.
    Note: places (graphs) and regions (stops) match i.e. contain the information relevant stops in the regions for the day(s).
    
    Parameters:
        places (list[dict] | dict): A list of dictionaries containing the place information or a single dictionary.
        regions (list[str]): A list of names regions stop files to calculate the isochrones for.
        days (list[int]): A list of days to calculate the isochrones for.
    """

    name = create_name(places)

    print(f"Calculating isochrones for batch (multiple days)")
    start_time = time.time()

    print(f"Loading graphs for {name}", end="\r")
    graph = load_graph(places)
    load_graph_time = time.time()
    print(f"Loaded graphs for {name} ..... {load_graph_time - start_time:.3f}s")
    print("--------------")

    for d in days:
        print(f"Calculating day {d}")
        time_before = time.time()
        
        print(f"Loading stops for {", ".join(regions)}", end="\r")
        stops = load_stops(regions, d)
        load_stops_time = time.time()
        print(f"Loaded stops for {", ".join(regions)} ..... {load_stops_time - time_before:.3f}s")
        
        print(f"Calculating isochrones for day {d}", end="\r")
        isochrones = calculate_isochrones(graph, stops, edge_snapping=edge_snapping)
        isochrones_time = time.time()
        print(f"Calculated isochrones for day {d} ..... {isochrones_time - load_stops_time:.3f}s")

        n = name + "_" + str(d)
        print(f"Saving isochrones to {PATH_ISOCHRONES_OUT}{n}.gpkg", end="\r")
        isochrones.to_file(f"{PATH_ISOCHRONES_OUT}{n}.gpkg", layer="isochrones", driver="GPKG")
        save_time = time.time()
        print(f"Saved isochrones to {PATH_ISOCHRONES_OUT}{n}.gpkg ..... {save_time - isochrones_time:.3f}s")
        print("--------------")


    #print(f"Finished calculation in {save_time - start_time:.3f}s\n\n")

    # TODO: add plot creation?? with higher resolution??
    # print(f"Drawing isochrones plot", end="\r")
    # fig, ax = draw_graph(graph, gdf=gdf, return_fig=True)
    # draw_time = time.time()
    # print(f"{"Drawn isochrones plot"} ..... {draw_time - isochrones_time:.3f}s")
    
    # print(f"Saving isochrones to {PATH_ISOCHRONES_OUT}{name}.gpkg and figure to {PATH_FIGS_OUT}{name}.png", end="\r")
    # isochrones.to_file(f"{PATH_ISOCHRONES_OUT}{name}.gpkg", layer="isochrones", driver="GPKG")
    # fig.savefig(f"{PATH_FIGS_OUT}{name}.png")
    # save_time = time.time()
    # print(f"Saved isochrones to {PATH_ISOCHRONES_OUT}{name}.gpkg and figure to {PATH_FIGS_OUT}{name}.png ..... {save_time - draw_time:.3f}s")

    # plt.figure(fig)
    # plt.show()


def run_calculation(place, region, day):
    start_time = time.time()

    print(f"Loading stops for {", ".join(region)}", end="\r")
    stops = load_stops(region, day)

    load_stops_time = time.time()
    print(f"Loaded stops for {", ".join(region)} ..... {load_stops_time - start_time:.3f}s")

    print(f"Loading graphs for {", ".join([p.get('state', p.get('city', "")) for p in place])}", end="\r")
    G = load_graph(place, save=True)
    load_graph_time = time.time()
    print(f"Loaded graphs for {", ".join([p.get('state', p.get('city', "")) for p in place])} ..... {load_graph_time - load_stops_time:.3f}s")

    #G = G[0] if len(G) == 1 else G

    print(f"Calculating isochrones", end="\r")
    isochrones = calculate_isochrones(G, stops)
    isochrones_time = time.time()
    print(f"{"Calculated isochrones"} ..... {isochrones_time - load_graph_time:.3f}s")

    #print(isochrones)

    # draw
    print(f"Drawing isochrones plot", end="\r")
    fig, ax = draw_graph(G, gdf=isochrones, return_fig=True)
    draw_time = time.time()
    print(f"{"Drawn isochrones plot"} ..... {draw_time - isochrones_time:.3f}s")

    name = create_name(place, simplify=simplify)
    name += "_" + str(day)

    print(f"Saving isochrones to {PATH_ISOCHRONES_OUT}{name}.gpkg and figure to {PATH_FIGS_OUT}{name}.png", end="\r")
    isochrones.to_file(f"{PATH_ISOCHRONES_OUT}{name}.gpkg", layer="isochrones", driver="GPKG")
    fig.savefig(f"{PATH_FIGS_OUT}{name}.png")
    save_time = time.time()
    print(f"Saved isochrones to {PATH_ISOCHRONES_OUT}{name}.gpkg and figure to {PATH_FIGS_OUT}{name}.png ..... {save_time - draw_time:.3f}s")

    print(f"Finished calculation in {save_time - start_time:.3f}s\n\n")
    plt.figure(fig)
    plt.show()

if __name__ == "__main__":
    #day = 20240528
    
    # region name for street network graph, e.g. {"city": "Vienna", "country": "Austria"}, 
    # use key "city" only for Vienna else "state", see top of file for list of regions
    #place = [{"state": "Tyrol", "country": "Austria"}, {"state": "Vorarlberg", "country": "Austria"}]

    # name of dfs in stops_dfs folder before "_{day}" e.g. "vor_obb"
    #region = ["vor_obb"]
    #region = ["vvt_vmobil_obb"]

    # batch calculation for multiple days
    places = PLACES
    regions = ["all_regions"]
    days = [20241023, 20241030]

    #print(create_name(places))

    calculate_batch_isochrones(places, regions, days, edge_snapping=False)
