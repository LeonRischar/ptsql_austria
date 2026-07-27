# ptsql_austria_calculator
  
# Description
This project contains the code to calculate the Public Transport Service Quality Levels (PTSQL) for Austria.

# Structure
```
ptsql_austria/
├── data/
│   ├── in/
│   │   ├── gtfs/            # folder to store the GTFS data for each region in subfolders
│   │   ├── oerok_solution/  # folder to store the oerok solution for for comparison with created solution
│   │   ├── osmnx_graphs/    # folder to store the osmnx street network graphs used for isochrone calculation
│   │   └── population_data/ # folder to store the population data for each region
│   └── out/
│       ├── evaluation/      # folder to store the evaluation results as dfs of area and population
│       ├── figs/            # folder to store figures of plots and isochrone examples
│       ├── isochrones/      # folder to store the created isochrones in geopackage format
│       └── stops/           # folder to store the created stop category dataframes 
├── src/                     # contains the code to calculate the PTSQL
└── docs/                    # contains more detailed documentation
```

# Dataset

### GTFS
The data used is from https://data.mobilitaetsverbuende.at/en/data-sets. Specifically, the GTFS data for the year 2024 is used. It is necessary to download the datasets for each region separately. 
The regions are:
- `Timetable Data PTA Eastern Region (GTFS)`- Eastern Region (VOR), contains Vienna, Lower Austria and Burgenland
- `Timetable Data PTA Upper Austria (GTFS)` - Upper Austria (OOEV), contains Upper Austria except Linz
- `Timetable Data Linz AG (GTFS)` - Linz (ESG)
- `Timetable Data PTA Styria (GTFS)` - Styria (Verbund Linie)
- `Timetable Data PTA Carinthia (GTFS)` - Carinthia (Kaernter Linien)
- `Timetable Data PTA Salzburg (GTFS)` - Salzburg (Salzburg Verkehr)
- `Timetable Data PTA Tyrol (GTFS)` - Tyrol (VVT)
- `Timetable Data PTA Vorarlberg (GTFS)` - Vorarlberg (VMOBIL)
- `Railway Timetable Data (GTFS) - Reference Data for Timetable Changeover` - Austria (OEBB), contains the national railway

For a detailed description of the GTFS data, please refer to `dataset_description.md` in the `/docs/` folder.

### OEROK
To compare the solution of this project to the existing solution of OEROK you need to add it to the `/data/in/oerok_solution` folder. 
Download `OeV_Gueteklassen_2024_nap.zip` from https://files.austriatech.at/d/33971b2d51a348a5958d/.
Extract the files for the two days 23 and 30 October with the name "Polygone" i.e. all files containing "Polygone" into the data folder.

### Population Grid
To do the population estimation, download the data from https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution/population-grids and extract it into `/data/in/population_data`.
The grid version used in this project is "Version 2021 (22 January 2025)". 
Move the folder "Eurostat_Census-GRID_2021_V2.2" as a whole, not the individual files inside.


# Requirements
See `requirements.txt` for the required python packages.  
The `requirements.txt` was generated using `pipreqs` with the following command:
```
  pipreqs --scan-notebooks --force --savepath ./requirements.txt ./src/
```

# Usage
1. Install packages from `requirements.txt`
1. Download the GTFS datasets as described in the dataset section and move them to the correct folder `/data/in/gtfs/`
2. Run the jupyter notebook `demo_categories_cleaned.ipynb` to calculate the stop categories. Or use the file `calculate_categories.py` (recommended).
3. Run the jupyter notebook `demo_isochrones_cleaned.ipynb` to create the isochrones. Or use the file `calculate_isochrones.py` (recommended). NOTE: this will download and save the OpenStreeMap (OSM) graphs by default.
4. Run the jupyter notebook `demo_evaluation.ipynb` to create the isochrones. Or use the file `evaluation.py`. NOTE: to run the full evaluation, you need the OEROK solution and population grid ready in their respective folder.
5. Configure the notebooks or file parameters as needed. E.g. regions, day, etc.

# Licenses
Please note that there are different licenses for different parts of this project:
- Input data: **Data License – Mobilitätsverbünde Österreich OG (License Agreement_DE_EN_DBP_v1.1)**, see `/data/in/`
- Output data: **Creative Commons Attribution 4.0 International** for everything in `/data/out/`
- Source code: **MIT License** for everything in `/src/` and documentation in `/docs/` as well as the rest of the project