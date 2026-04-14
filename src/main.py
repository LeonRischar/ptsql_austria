from calculate_categories import run_category_calculation
from calculate_isochrones import run_isochrone_calculation
from evaluation import run_evaluation
from config import *


# IMPORTANT: for parameter settings, please check config.py

def main():

    # Step 1: Calculate rank interval for all regions and days
    run_category_calculation(regions=list(GTFS_REGIONS.keys()), days=ALL_DAYS) 

    # Step 2: Calculate isochrones for all regions and days
    run_isochrone_calculation(region_graphs=GRAPH_REGIONS, region_stops=list(GTFS_REGIONS.keys()), days=ALL_DAYS)

    # Step 3: Run evaluation
    run_evaluation()


if __name__ == "__main__":
    main()