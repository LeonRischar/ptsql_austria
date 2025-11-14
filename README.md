# ptsql

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
- data/:
  - in/: contains the original data in GTFS format for all of Austria (the data is NOT provided in this repo, refer to the dataset description for more information)
  - out/: contains the generated output files
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
2. Place the unzipped datasets in the `/data/in/` folder
3. Run the jupyter notebook to calculate the PTSQL.

# License
Please not that there are different licenses for different parts of this project:
- Input data: **Data License – Mobilitätsverbünde Österreich OG (License Agreement_DE_EN_DBP_v1.1)**, see `/data/in/`
- Output data: **Creative Commons Attribution 4.0 International** for everything in `/data/out/`
- Source code: **MIT License** for everything in `/src/` and documentation in `/docs/` as well as the rest of the project