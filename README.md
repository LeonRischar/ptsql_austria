# ptsql

## TODO:
- add Licence
- improve README
  - structure
  - usage
- add dataset description
- add requirements.txt
  
# Description
This repo contains the code to calculate the PTSQL in Austria.

# Structure
- data/: contains the data in GTFS format for all of Austria
- src/: contains the code to calculate the PTSQL
- docs/: contains more detailed documentation

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

# Usage
1. Download the datasets described above
2. Place the unzipped datasets in the data folder in the root of the project
3. Run the jupyter notebook to calculate the PTSQL.