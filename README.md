# ptsql_austria_calculator

## TODO:
- add Licence
- improve README
  - structure
  - usage
- add dataset description
- add requirements.txt
  
# Description
This project contains the code to calculate the Public Transport Service Quality Levels (PTSQL) for Austria.

# Structure
```
ptsql_austria/
├── data/
│   ├── in/   # contains the original data in GTFS format for all of Austria (the data is NOT provided in this repo, refer to the dataset description for more information)
        └── osmnx_graphs/  # folder to store the osmnx street network graphs used for isochrone calculation
│   └── out/
│       ├── figs/  # folder to store figures of the isochrones
│       ├── isochrones_gpkg/  # folder to store the created isochrones in geopackage format
│       └── stop_dfs/  # folder to store the created stop dataframes 
├── src/      # contains the code to calculate the PTSQL
└── docs/     # contains more detailed documentation
```

# Dataset
The data used is from https://data.mobilitaetsverbuende.at/en/data-sets. Specifically, the GTFS data for the year 2024 is used. It is necessary to download the datasets for each region (almost like states) separately. 
The region are:
- Eastern Region (VOR) contains Vienna, Lower Austria and Burgenland
- Upper Austria (OOEV) contains Upper Austria except Linz
- Linz (ESG) contains Linz
- Styria (Verbund Linie) contains Styria
- Carinthia (Kaernter Linien) contains Carinthia
- Salzburg (Salzburg Verkehr) contains Salzburg
- Tyrol (VVT) contains Tyrol
- Vorarlberg (VMOBIL) contains Vorarlberg
The datasets contain the information about the local public transportation in the respective region. Data for the national railway (OEBB) is not included and must downloaded separately.
- Austria (OEBB) contains the national railway (Railway Timetable Data (GTFS) - Reference Data for Timetable Changeover)

For a detailed description of the data, please refer to `dataset_description.md` in the `/docs/` folder.

# Requirements
See `requirements.txt` for the required python packages.
The `requirements.txt` was generated using `pipreqs` with the following command:
```
  pipreqs --scan-notebooks --force --savepath ./requirements.txt ./src/
```
For requirements to use QGIS, see `usage_qgis.md` in the `/docs/` folder.

# Usage
## How to use the Jupyter Notebooks and Python files
1. Download the datasets described in the dataset section
2. Place the unzipped datasets for each region in the `/data/in/` folder
3. Run the jupyter notebook `test_categories_cleaned.ipynb` to calculate the stop categories. Or use the file `calculate_categories.py` (recommended).
4. Run the jupyter notebook `test_isochrones_cleaned.ipynb` to create the isochrones. Or use the file `calculate_isochrones.py` (recommended).
5. Configure the notebooks or file parameters as needed. E.g. regions, day, etc.

## How to use QGIS
For a description of how to use QGIS with the created files, please refer to the `usage_qgis.md` file in the `/docs/` folder.

# License
Please note that there are different licenses for different parts of this project:
- Input data: **Data License – Mobilitätsverbünde Österreich OG (License Agreement_DE_EN_DBP_v1.1)**, see `/data/in/`
- Output data: **Creative Commons Attribution 4.0 International** for everything in `/data/out/`
- Source code: **MIT License** for everything in `/src/` and documentation in `/docs/` as well as the rest of the project