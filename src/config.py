import numpy as np

# configs and constants

# Options for isochrone calculation, these are the most useful to change
# the other configs can be changed as well, but probably need more adaptations by the user

# days used for evaluation
WEEKDAYS = [20240131, 20240215, 20240315, 20240415, 20240515, 20240614, 20240715, 20240814, 20240916, 20241015, 20241115, 20241213]
OEROK_DAYS = [20241023, 20241030]
WEEKENDS = [20240210, 20240414, 20240608, 20240811, 20241012, 20241208]
ALL_DAYS = WEEKDAYS + OEROK_DAYS + WEEKENDS

# other days to plot with oreok solution for comparison, must be from already specified days
OTHER_DAYS = [20241012, 20241015]

# snap stop locations to nearest edge
# options: "all", "partial", "none" - default: "partial"
EDGE_SNAPPING = "partial" 

# max distance in meters to use nearest node otherwise use edge snapping, only used if EDGE_SNAPPING is "partial"
NEAREST_NODE_THRESHOLD = 50 # default: 50

# create buffer around isochrones to smoothen, increases isochrone size, in meters
BUFFER = 25 # default: 25

# paths for input data
PATH_IN_GTFS = "../data/in/gtfs/"
PATH_IN_GRAPHS = "../data/in/osmnx_graphs/"
PATH_IN_POPULATION = "../data/in/population_data/"
PATH_IN_OEROK = "../data/in/oerok_solution/"

# path for output data i.e. data produced by this project
PATH_OUT_ISOCHRONES = "../data/out/isochrones/"
PATH_OUT_STOPS = "../data/out/stops/"
PATH_OUT_EVALUATION = "../data/out/evaluation/"
PATH_OUT_FIGS = "../data/out/figs/"

# name of population file to use for evaluation, should be placed in PATH_IN_POPULATION or subfolders
# default: "Eurostat_Census-GRID_2021_V2.2/ESTAT_Census_2021_V2.gpkg"
POPULATION_FILE = "Eurostat_Census-GRID_2021_V2.2/ESTAT_Census_2021_V2.gpkg"

# name scheme of oerok solution files, should be placed in PATH_IN_OEROK or subfolders
# {} will be replaced by day1 and day2 in prepare_oerok_data function
OEROK_NAME_SCHEME = "OeV_Gueteklassen_Polygone_{}.shp" # default: "OeV_Gueteklassen_Polygone_{}.shp"

# exact names of GTFS folders in PATH_IN_GTFS for each region
GTFS_REGIONS = {"vor": "20241214-0617_gtfs_vor_2024", #vienna, lower austria, burgenland
           "ooevv": "20241212-0156_gtfs_ooevv_2024", #upper austria
           "esg": "20241203-0058_gtfs_esg_2024", #linz
           "verbundlinie": "20241217-0310_gtfs_verbundlinie_2024", #styria
           "kaernterlinien": "20241214-0253_gtfs_kaerntnerlinien_2024", #carinthia
           "salzburgverkehr": "20241217-0359_gtfs_salzburgverkehr_2024", #salzburg
           "vvt": "20241217-0436_gtfs_vvt_2024", #tyrol
           "vmobil": "20241212-0624_gtfs_vmobil_2024", #vorarlberg
           "obb": "GTFS_2024_obb"} #oebb maybe 20241217-0222_gtfs_evu_2024

# transport_category = ["Fernverkehr REX", 
#                       "S-Bahn / U-Bahn, Regionalbahn, Schnellbus, Lokalbahn", 
#                       "Straßenbahn, Metrobus, 0-Bus", 
#                       "Bus"]
# translates other route types to appropriate transport category defined by OEROK
ROUTE_TYPE_TRANSLATION = {0: 2, 1: 1, 2: 0, 3: 3, 11: 3,}

# table defined by OEROK for stop categories based on interval and transport type
STOP_CATEGORY_TABLE = np.array([
    [0, 0, 0, 0],        # < 5 min
    [0, 1, 2, 2],        # 5 >= x <= 10
    [1, 2, 3, 3],        # 10 < x < 20
    [2, 3, 4, 4],        # 20 >= x < 40
    [3, 4, 5, 5],        # 40 >= x <= 60
    [4, 5, 6, 6],        # 60 < x <= 120  
    [-1, 6, 7, 7],       # 120 < x <= 210 
    [-1, -1, -1, -1],    # > 210
])

# stop categories in roman numerals (not used currently)
TABLE_ROMAN = np.array([
    ["I", "I", "II", "III"],        # < 5 min
    ["I", "II", "III", "III"],      # 5 >= x <= 10
    ["II", "III", "IV", "IV"],      # 10 < x < 20
    ["III", "IV", "V", "V"],        # 20 >= x < 40
    ["IV", "V", "VI", "VI"],        # 40 >= x <= 60
    ["V", "VI", "VII", "VII"],      # 60 < x <= 120  
    ["X", "VII", "VIII", "VIII"],    # 120 < x <= 210 
    ["X", "X", "X", "X"],               # > 210 
                                    # X = empty, i.e. worst case
])


GRAPH_REGIONS = [{"city": "Vienna", "country": "Austria"},
                {"state": "Lower Austria", "country": "Austria"},
                {"state": "Upper Austria", "country": "Austria"},
                {"state": "Burgenland", "country": "Austria"},
                {"state": "Salzburg", "country": "Austria"},
                {"state": "Styria", "country": "Austria"},
                {"state": "Carinthia", "country": "Austria"},
                {"state": "Tyrol", "country": "Austria"},
                {"county": "Lienz", "state": "Tyrol", "country": "Austria"}, # special case for eastern tyrol
                {"state": "Vorarlberg", "country": "Austria"}]

# crs of input data e.g. GTFS
SOURCE_CRS = "epsg:4326" # default: "epsg:4326"

# crs of output data e.g. isochrones and stops dfs
TARGET_CRS = "epsg:31287" # default: "epsg:31287"

# network type for osmnx
NETWORK_TYPE = "walk" # default: "walk"

# distances and colors used for isochrones
DISTANCES = [300, 500, 750, 1000, 1250]
PTSQL_COLORS = ["#E42421", "#E95153", "#E63C1E", "#F29668", "#34672B", "#87C281", "#959595", "none"]
PTSQL_COLORS_DICT = {"A":"#E42421", "B":"#E95153", "C":"#E63C1E", "D":"#F29668", "E":"#34672B", "F":"#87C281", "G":"#959595", "H":"none"}

# translate rank and interval to PTSQL color
PTSQL_COLOR_TABLE = [[0,0,1,2,3], # I
                    [0,1,2,3,4], # II
                    [1,2,3,4,5], # III
                    [2,3,4,5,6], # IV
                    [3,4,5,6,6], # V
                    [4,5,6,-1,-1], # VI
                    [5,6,6,-1,-1], # VII
                    [6,6,-1,-1,-1]] # VIII

# boundaries of Austria in EPSG:3035 in meters for directions north (N) and east (E)
MIN_E = 3850000
MAX_E = 4850000
MIN_N = 2250000
MAX_N = 3150000