''' For some reason, the data portal doesn't let you download the current ward boundaries as a geoJSON file.
This script calls the data portal URL using a geoJSON extension and then saves that file to this folder.'''

import geopandas as gpd

current_wards = gpd.read_file('https://data.cityofchicago.org/resource/p293-wvbd.geojson')
#Test to confirm output
print(current_wards)
#Uncomment to save to file
#current_wards.to_file('wards_23_.geojson')