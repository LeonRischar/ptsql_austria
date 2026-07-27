import time
import warnings

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

import regex as re
from datetime import datetime

from config import *


def lookup_category(interval, t_cat):
    """
    Lookup the stop category based on the interval and the transport type.
    """
    if interval < 5:
        return STOP_CATEGORY_TABLE[0][t_cat]
    elif interval <= 10:
        return STOP_CATEGORY_TABLE[1][t_cat]
    elif interval < 20:
        return STOP_CATEGORY_TABLE[2][t_cat]
    elif interval < 40:
        return STOP_CATEGORY_TABLE[3][t_cat]
    elif interval <= 60:
        return STOP_CATEGORY_TABLE[4][t_cat]
    elif interval <= 120:
        return STOP_CATEGORY_TABLE[5][t_cat]
    elif interval <= 210:
        return STOP_CATEGORY_TABLE[6][t_cat]
    else:
        return STOP_CATEGORY_TABLE[7][t_cat]
    
def category_to_roman(t_cat, reverse=False):
    """
    Convert a category to a roman numeral or vice versa if reverse is True
    """
    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "X"]
    if reverse:
        return roman_numerals.index(t_cat)
    return roman_numerals[t_cat]
    
def detect_route_type(trip_name, route_type):
    """
    Detect the type of transportation based on the trip name and the route type
    By default, the transport type is only based on the route type.
    For route type 2 (train), the trip_name is used, to further distinguish between different trains, if available.
    """
    # TODO: also consider route_short/long_name ??? 
    if route_type == 2 and not pd.isna(trip_name):
        trips_name = trip_name.lower()
        if any(x in trips_name for x in ["rj", "rjx", "nj", "en", "ic", "ec", "ice", "ecb", "rex", "wb", "rgj", "cjx" ]): #fernverkehr, long distance trains
            return 0
        else:
            return 1
    else:
        return ROUTE_TYPE_TRANSLATION[route_type]

def calculate_rank_interval_for_single_region(state_name: str, selected_day: int) -> pd.DataFrame:
    """
    Calculate the rank and interval for the specified region and day.

    Parameters:
        state_name (str): The name of the region to calculate the rank and interval for.
        selected_day (int): The day for which the categories should be calculated in the format YYYYMMDD.

    Returns:
        pd.DataFrame: A DataFrame containing the rank and interval for the specified region and day.    
    """

    # load data

    path = PATH_IN_GTFS +  GTFS_REGIONS[state_name]

    stops = pd.read_csv(path + "/stops.txt", quotechar='"', sep=",")
    stop_times = pd.read_csv(path + "/stop_times.txt", quotechar='"', sep=",")
    trips = pd.read_csv(path + "/trips.txt", quotechar='"', sep=",")
    routes = pd.read_csv(path + "/routes.txt", quotechar='"', sep=",")
    calendar = pd.read_csv(path + "/calendar.txt", quotechar='"', sep=",")
    calendar_dates = pd.read_csv(path + "/calendar_dates.txt", quotechar='"', sep=",")

    # filter calendar and calendar_dates

    # find weekday of selected day
    date = datetime.fromisoformat(str(selected_day))
    day_string = date.strftime("%A").lower()

    # only keep services that run on the selected day and weekday
    calendar_filtered = calendar[(calendar['start_date'] <= selected_day) & (calendar['end_date'] >= selected_day) & (calendar[day_string] == 1)].copy()
    
    # select services from exceptions
    added_service = calendar_dates[(calendar_dates['date'] == selected_day) & (calendar_dates['exception_type'] == 1)]
    removed_service = calendar_dates[(calendar_dates['date'] == selected_day) & (calendar_dates['exception_type'] == 2)]

    # filter to keep only valid trips
    trips_filtered = trips[trips['service_id'].isin(calendar_filtered['service_id'])]

    # remove services with exception_type = 2 from calendar_dates
    trips_filtered = trips_filtered[~trips_filtered["service_id"].isin(removed_service["service_id"])]

    # add services with exception_type = 1 from calendar_dates
    trips_full = pd.concat([trips_filtered, trips[trips["service_id"].isin(added_service["service_id"])]])

    if trips_full.shape[0] == 0:
        print(f"No trips found for {state_name} on {selected_day}! Either no service is running on this day or the input data is incomplete/incorrect.")
        return pd.DataFrame()

    # merge trips and routes

    # merge trips with routes information
    routes_trips = pd.merge(trips_full, routes, on='route_id', how='left')

    routes_trips = routes_trips[routes_trips['route_type'].isin(ROUTE_TYPE_TRANSLATION.keys())]

    # translate route type
    routes_trips['trip_short_name'] = routes_trips['trip_short_name'].astype('str')
    routes_trips['rank'] = routes_trips.apply(lambda x: detect_route_type(x['trip_short_name'], x['route_type']), axis=1)

    #prepare stops and stop_times
    stops_filtered = stops.copy()
    stops_filtered['stop_id'] = stops_filtered['stop_id'].astype(str).apply(
        lambda x: (
            re.match(r'^((?:[^:]*:){3})', x).group(1).rstrip(':')
            if re.match(r'^((?:[^:]*:){3})', x)
            else x
        )
    )
    # keep only stop entry for parent station, if no parent station is given, keep a stop entry
    stops_parents = stops_filtered[stops_filtered['stop_id'].str.startswith('Pat')].copy()
    stops_parents['stop_id'] = stops_parents['stop_id'].apply(lambda x: x if x[0] != 'P' else x[1:])
    stops_filtered = stops_filtered[stops_filtered['stop_id'].str.startswith('at') | stops_filtered['stop_id'].str.startswith('obb')]
    stops_filtered = stops_filtered[~stops_filtered['stop_id'].isin(stops_parents['stop_id'])].drop_duplicates(subset=['stop_id'], keep='first')
    stops_filtered_final = pd.concat([stops_parents, stops_filtered])

    stop_times_filtered = stop_times.copy()
    stop_times_filtered = stop_times_filtered[stop_times_filtered['departure_time'].between('06:00:00', '20:00:00')]
    stop_times_filtered = stop_times_filtered[stop_times_filtered['stop_id'].str.startswith('at')]

    stop_times_filtered['stop_id'] = stop_times_filtered['stop_id'].astype(str).apply(
        lambda x: (
            re.match(r'^((?:[^:]*:){3})', x).group(1).rstrip(':')
            if re.match(r'^((?:[^:]*:){3})', x)
            else x
        )
    )

    # add trip and route information to stop_times
    stop_times_trips = pd.merge(stop_times_filtered, routes_trips, on='trip_id', how='inner')

    # calculate rank intervals
    stop_times_grouped = stop_times_trips.groupby(['stop_id']).agg(rank=("rank", "min"), count=("rank", "count")).reset_index().copy()

    # merge with stops and kepp only needed columns
    stops_final = pd.merge(stops_filtered_final.drop(['zone_id', 'location_type', 'level_id', 'platform_code', 'parent_station'], axis=1), stop_times_grouped, on='stop_id', how='inner')

    return stops_final

def calculate_rank_interval_for_all_regions(selected_day: int, selected_regions: list[str] = None):
    """
    Calculate the category (rank, interval) for all stations in the regions for the selected_day.
    If selected_regions is None, calculate for all regions.

    Parameters:
        selected_day (int): The day for which the categories should be calculated in the format YYYYMMDD.
        selected_regions (list[str]): A list of regions for which the categories should be calculated. If None, calculate for all regions.

    Returns:
        None
    """

    state_dfs = []
    total_time = 0

    selected_regions = list(GTFS_REGIONS.keys()) if selected_regions is None else selected_regions

    print(f"Calculating regions: ")
    for state_name in selected_regions:
        print(f"{state_name}", end="\r")
        start_time = time.time()
        
        state_dfs.append(calculate_rank_interval_for_single_region(state_name, selected_day))

        elapsed = time.time() - start_time
        total_time += elapsed
        print(f"{state_name:<20} {elapsed:.3f}s")


    print(f"Total time: {total_time:.3f}s")

    # merge all state dfs
    all_regions = pd.concat(state_dfs)
    agg = all_regions.groupby(['stop_id']).agg(rank=("rank", "min"), count=("count", "sum")).reset_index()

    # all_regions = pd.merge(agg, all_regions[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], on='stop_id', how='left')
    all_regions = pd.merge(all_regions[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']], agg, on='stop_id', how='right')

    # calculate intervals and station categories
    all_regions["interval"] = all_regions["count"].apply(lambda x: 840 / (x/2) if x != 0 else 1680)
    all_regions["category"] = all_regions.apply(lambda x: lookup_category(x["interval"], x["rank"]), axis=1)

    # drop duplicates arising slightly different coords for same stop
    all_regions = all_regions.drop_duplicates(subset=['stop_id'], keep='first')

    # print infos
    print(f"Number of stops: {len(all_regions)}")

    # save to file
    f_name = f"all_regions_{selected_day}.csv" if selected_regions == list(GTFS_REGIONS.keys()) else f"{'_'.join(selected_regions)}_{selected_day}.csv"
    all_regions.to_csv(PATH_OUT_STOPS + f_name, index=False)
    print(f"\nSaved to {PATH_OUT_STOPS + f_name}")


def run_category_calculation(regions: list[str] = None, days: list[int] = ALL_DAYS):
    """
    Run the calculation of rank and interval for all specified regions and days.
    """
    if regions is None:
        regions = list(GTFS_REGIONS.keys())

    print(f"Running category calculation for {len(regions)} regions and {len(days)} days")

    # run calculation for each day for all selected regions as one
    for d in days:
        print(f"Calculating categories for day {d}")

        calculate_rank_interval_for_all_regions(d, regions)

        print("--------------\n")


if __name__ == "__main__":
    # default: calculate for all regions and all days (from config.py)
    run_category_calculation()
