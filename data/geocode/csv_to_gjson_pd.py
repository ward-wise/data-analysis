import geopandas as gpd
import pandas as pd
from shapely import Point

df = pd.read_csv("geocode/Address_Points_reduced.csv")  # Specify file path for CSV input

geometry = [Point(xy) for xy in zip(df["Long"], df["Lat"], strict=False)]
crs = "EPSG:4326"  # Specify coordinate reference system--see geopandas docs.
gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
# Rename columns if necessary.
# These columns will show up as a "property" of each coordinate in the geoJSON file,
# so clear labeling will be helpful.
gdf = gdf.rename(columns={"CMPADDABRV": "Address", "Unnamed: 0": "ID"})
# Drop redundant Latitude and Longitude columns if necessary. This massively reduces the file size.
gdf = gdf.drop(columns=["Lat", "Long"])

gdf.to_file(
    "geocode/address_points.geojson", driver="GeoJSON"
)  # Specify file path for geoJSON output
