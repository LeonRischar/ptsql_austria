# ptsql_austria
  
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
To use the code and replicate the results it is necessary to download and add the required data in the respective folders as indicated in the `Structure` section. 

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

### OpenStreetMap
The walkable paths network used to perform the routing calculations for the PTSQL creation comes from OpenStreetMap (https://www.openstreetmap.org).
It is automatically downloaded throught the `osmnx` Python package into `/data/in/osmnx_graphs`.

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

# Licenses and Attributions
Please note that there are different licenses for different parts of this project:
- Input data in `data/in/`: 
  - `gtfs`: 
    - Data source: Mobilitätsverbünde Österreich OG - data.moblitaetsverbuende.at
    - License: Mobilitätsverbünde Österreich OG - License Agreement_DE_EN_DBP_v1.1, see `data/in/gtfs` for license pdf
  - `oerok_solution`: 
    - Data source: AustriaTech - https://www.mobilitydata.gv.at/en/daten/%C3%B6v-g%C3%BCteklassen
    - Data usage - Disclaimer: https://www.oerok.gv.at/raum/themen/raumordnung-und-mobilitaet
  - `osmnx_graphs`: 
    - Data Source: OpenStreetMap - https://www.openstreetmap.org/copyright/en
    - License: Open Data Commons Open Database License (ODbL) - https://opendatacommons.org/licenses/odbl/summary/
  - `population_data`: 
    - Data Source: Eurostat - https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution/population-grids
    - License: CC-BY 4.0 - https://creativecommons.org/licenses/by/4.0/deed.en
- Output data: **Creative Commons Attribution 4.0 International** for everything in `/data/out/`
- Source code: **MIT License** for everything in `/src/` and documentation in `/docs/` as well as the rest of the project

# Licenses and Attributions

This repository contains code, documentation, and third-party data
distributed under different terms.

## Source code and documentation

Unless otherwise stated, the source code in `src/`, documentation in
`docs/`, and other original project materials are licensed under the
MIT License. See [`LICENSE`](LICENSE).

## Input data

The input datasets are not covered by the MIT License.
Their terms are as follows:

- `data/in/gtfs/`: 
  - Data source: Mobilitätsverbünde Österreich OG - data.moblitaetsverbuende.at (https://data.mobilitaetsverbuende.at/de/data-sets)
  - License: the license agreement included in that directory. See [`License Agreement_DE_EN_DBP_v1.1`](data/in/gtfs/License%20Agreement_DE_EN_DBP_v1.1.pdf)
- `data/in/oerok_solution/`: 
  - Data source: AustriaTech/OEROK (https://www.mobilitydata.gv.at/en/daten/%C3%B6v-g%C3%BCteklassen). 
  - License: Disclaimer information in that directory. See [`Data Usage - Disclaimer`](data/in/oerok_solution/DISCLAIMER.txt)
- `data/in/osmnx_graphs/`: 
  - Data source: OpenStreetMap (https://www.openstreetmap.org/copyright/en), via `osmnx` Python package 
  - License: Open Database License (ODbL). See license file in that directory [`Open Database License (ODbL)`](data/in/osmnx_graphs/LICENSE)
- `data/in/population_data/`:
  - Data source: Eurostat - https://ec.europa.eu/eurostat/web/gisco/geodata/population-distribution/population-grids
  - License: available under CC BY 4.0. See the license file in that directory [`CC BY 4.0`](data/in/population_data/LICENSE).

## Changes to Input data
The source datasets were not directly modified or redistributed. They were used as inputs to generate derived outputs through the following operations:
- **GTFS**: Public transport stops were assigned intervals and ranks according to the OEROK methodology. The stop coordinates were also used in subsequent calculations.
- **OpenStreetMap**: OSM road-network graphs were used to calculate walkable routes to public transport stops and to generate isochrones—polygons representing areas reachable within specified travel-time intervals. The OSM graphs were reprojected to a different coordinate reference system (CRS) for these calculations.
- **OEROK solution**: The existing OEROK solution was used to compare and validate the results of this project. For this comparison, the areas and populations covered by the OEROK isochrones were calculated.
- **Population data**: Population-grid data was used to estimate the population covered by the generated isochrones.

## Output data

The output data in `data/out/` is intended to be made available under
CC BY 4.0, except for any portions whose source terms impose additional
or incompatible conditions. See [`data/out/LICENSE`](data/out/LICENSE).
