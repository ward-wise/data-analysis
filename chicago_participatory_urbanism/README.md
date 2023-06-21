# Geocoder Setup

The geocoder package requires two files to run, linked in the file and here:
* [Cook County Address Point Data](https://hub-cookcountyil.opendata.arcgis.com/datasets/5ec856ded93e4f85b3f6e1bc027a2472_0/about)
* [Chicago Street Center Lines GeoJSON](https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau)

Download these files and place them in `data/geocode`.

It takes a long time for the data to load into memory (approx. 90 seconds). After they're in memory, all the functions run very quickly.