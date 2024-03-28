import pandas as pd
from shapely import Point
import geopandas as gpd


df = pd.read_csv('geocode/Address_Points_reduced.csv') #Specify file path for CSV input

geometry = [Point(xy) for xy in zip(self.address_points_df['Long'], self.address_points_df['Lat'])]
crs = 'EPSG:4326' #Specify coordinate reference system--see geopandas docs.
self.street_center_lines_gdf = gpd.GeoDataFrame(self.address_points_df, crs=crs, geometry=geometry)
#Rename columns if necessary. These columns will show up as a "property" of each coordinate in the geoJSON file, so clear labeling will be helpful.
self.street_center_lines_gdf = self.street_center_lines_gdf.rename(columns={'CMPADDABRV': 'Address', 'Unnamed: 0': 'ID'})
#Drop redundant Latitude and Longitude columns if necessary. This massively reduces the file size.
self.street_center_lines_gdf = self.street_center_lines_gdf.drop(columns=['Lat', 'Long'])

self.street_center_lines_gdf.to_file('geocode/address_points.geojson', driver="GeoJSON") #Specify file path for geoJSON output