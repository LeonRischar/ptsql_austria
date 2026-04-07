import numpy as np

# configs and constants

# days used for evaluation
WEEKDAYS = [20240131, 20240215, 20240315, 20240415, 20240515, 20240614, 20240715, 20240814, 20240916, 20241015, 20241115, 20241213]
OEROK_DAYS = [20241023, 20241030]
WEEKENDS = [20240210, 20240414, 20240608, 20240811, 20241012, 20241208]
ALL_DAYS = WEEKDAYS + OEROK_DAYS + WEEKENDS

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

# network type for osmnx
NETWORK_TYPE = "walk"

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

SOURCE_CRS = "epsg:4326" # crs of input data e.g. GTFS
TARGET_CRS = "epsg:31287" # crs of output data e.g. isochrones and stops dfs

# distances and colors used for isochrones
DISTANCES = [300, 500, 750, 1000, 1250]
PTSQL_COLORS = ["#E42421", "#E95153", "#E63C1E", "#F29668", "#34672B", "#87C281", "#959595", "none"]
PTSQL_COLORS_DICT = {"A":"#E42421", "B":"#E95153", "C":"#E63C1E", "D":"#F29668", "E":"#34672B", "F":"#87C281", "G":"#959595", "H":"none"}

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