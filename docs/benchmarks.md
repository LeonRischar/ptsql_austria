# Benchmarks

## Times for VOR region:
```
  Loaded stops for vor_obb ..... 0.022s
  Loaded graphs for Vienna, Lower Austria, Burgenland ..... 82.362s
  Calculated isochrones ..... 32.584s
  Drawn isochrones plot ..... 43.627s
```

## Times for all regions:
```
  Loaded stops for all_regions ..... 0.040s
  Loaded graphs for Vienna, Lower Austria, Upper Austria, Burgenland, Salzburg, Styria, Carinthia, Tyrol, Vorarlberg ..... 413.314s
  Calculated isochrones ..... 91.569s
  Drawn isochrones plot ..... 213.108s
  Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20240528.gpkg and figure to ../data/out/figs/all_regions_20240528.png ..... 14.362s
```

## times for all regions on 6 days 
```
Calculating batch isochrones in parallel
Loaded graphs for all_regions ..... 311.892s       
Calculating day 20240210
Loaded stops for all_regions ..... 0.034s
Calculated isochrones for day 20240210 ..... 53.231s
Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20240210.gpkg ..... 0.270s
--------------

Calculating day 20240410
Loaded stops for all_regions ..... 0.042s
Calculated isochrones for day 20240410 ..... 70.332s
Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20240410.gpkg ..... 0.150s
--------------

Calculating day 20240610
Loaded stops for all_regions ..... 0.047s
Calculated isochrones for day 20240610 ..... 69.941s
Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20240610.gpkg ..... 0.146s
--------------

Calculating day 20240810
Loaded stops for all_regions ..... 0.034s
Calculated isochrones for day 20240810 ..... 52.966s
Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20240810.gpkg ..... 0.102s
--------------

Calculating day 20241010
Loaded stops for all_regions ..... 0.042s
Calculated isochrones for day 20241010 ..... 71.496s
Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20241010.gpkg ..... 0.148s
--------------

Calculating day 20241210
Loaded stops for all_regions ..... 0.046s
Calculated isochrones for day 20241210 ..... 72.523s
Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20241210.gpkg ..... 0.146s
--------------
```

## times for all regions and the 2 days used in existing solution (23.10. and 30.10.)
```
Calculating batch isochrones in parallel
Loaded graphs for all_regions ..... 480.192s       
Calculating day 20241023
Loaded stops for all_regions ..... 0.053s
Calculated isochrones for day 20241023 ..... 74.749s
Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20241023.gpkg ..... 0.272s
--------------

Calculating day 20241030
Loaded stops for all_regions ..... 0.048s
Calculated isochrones for day 20241030 ..... 67.454s
Saved isochrones to ../data/out/isochrones_gpkg/all_regions_20241030.gpkg ..... 0.157s
--------------
```