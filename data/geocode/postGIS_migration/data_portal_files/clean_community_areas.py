import geopandas as gpd

file = gpd.read_file('orig_files/community_areas.geojson')

#Create empty geoDataFrame for new format
empty_cols = {'community_area': [], 'the_geom': []}
gdf = gpd.GeoDataFrame(empty_cols, geometry='the_geom', crs='EPSG:4326')
#Fill columns in new geoDataFrame using appropriate column names from original file
gdf['community_area'] = file['community']
gdf['the_geom'] = file['geometry']

gdf.to_file('clean_files/cl_community_areas.geojson')