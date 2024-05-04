'''Each ward boundary file uses different data fields, many of which are unnecessary or redundant for our purposes.
This script uses geopandas to clean each file and return a geojson file with two columns: ward (the ward number) and the_geom (the coordinates needed to map the ward boundary).'''

import geopandas as gpd

#Read original data portal file
file = gpd.read_file('orig_ward_files/wards_23_.geojson')
#Create empty geoDataFrame for new format
empty_cols = {'ward': [], 'the_geom': []}
gdf = gpd.GeoDataFrame(empty_cols, geometry='the_geom', crs='EPSG:4326')
#Fill columns in new geoDataFrame using appropriate column names from original file
gdf['ward'] = file['ward']
gdf['the_geom'] = file['geometry']
#Drop rows if needed (an issue with 03-15 data)
gdf = gdf.drop(gdf[gdf.ward == 'OUT'].index)
#Save new geoDataFrame as geojson
gdf.to_file('clean_files/cl_wards_23_.geojson')