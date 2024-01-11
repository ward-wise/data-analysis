import pandas as pd
from shapely import Point
import geopandas as gpd


df = pd.read_csv(path) #Specify file path for CSV input

geometry = [Point(xy) for xy in zip(df['Long'], df['Lat'])]
crs = 'EPSG:4326' #Specify coordinate reference system--see geopandas docs.
gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
#Rename columns if necessary. These columns will show up as a "property" of each coordinate in the geoJSON file, so clear labeling will be helpful.
gdf = gdf.rename(columns={'CMPADDABRV':'Address', 'Unnamed: 0':'ID'}) 

gdf.to_file(path, driver="GeoJSON") #Specify file path for geoJSON output

