# Dataset description

The full specification can be found [here](https://gtfs.org/documentation/schedule/reference/).

## GTFS
GTFS stands for General Transit Feed Specification. It is a standard format introduced by Google to describe public transportation systems.

## Important files and fields
- `stops.txt`: contains the stops of the public transportation system
  - **stop_id**: unique identifier of the stop, shared with `stop_times.txt`
  - **stop_name**: humnan-readable name of the stop
  - **parent_station**: identifier of the parent station, to group stops into stations, e.g. bus stop is at a different location than the metro stop but belong to the same station
  - **stop_lat**, **stop_lon**: the latitude and longitude of the stop
- `stop_times.txt`: contains the schedule of the public transportation system
  - **stop_id**: unique identifier of the stop, shared with `stops.txt`
  - **trip_id**: unique identifier of the trip, shared with `trips.txt`
- `trips.txt`: contains the trips. a trip is one vehicle that travels a whole route, turning at the last stop is considered a separate trip
  - **departure_time**: the time the vehicle leaves the stop
  - **trip_id**: unique identifier of the trip, shared with `stop_times.txt`
  - **route_id**: unique identifier of the route, shared with `routes.txt`
  - **service_id**: unique identifier of the service, shared with `calendar.txt`
- `calendar.txt`: contains for each service the days of the week when the service is active
  - **service_id**: unique identifier of the service, shared with `trips.txt`
  - **start_date**, **end_date**: between which dates the entry is valid
  - weekdays: 0 or 1, indicating if the service is active on the corresponding day
- `calendar_dates.txt`: contains exceptions to the calendar
  - **service_id**: unique identifier of the service, shared with `calendar.txt`
  - **date**: specific day of the exception in the format `YYYYMMDD`
  -  **exception_type**: 1 - service added, 2 - service removed
- `routes.txt`: contains the routes of the public transportation system
  - **route_id**: unique identifier of the route, shared with `trips.txt`
  - **route_type**: 0 - Tram, 1 - Subway, 2 - Rail, 3 - Bus, for more see https://gtfs.org/documentation/schedule/reference/#routestxt

