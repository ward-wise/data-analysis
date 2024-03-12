import pandas as pd
import importlib.metadata
import logging
import geopandas as gpd
from shapely.ops import unary_union
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString
from src.chicago_participatory_urbanism.location_structures import (
    StreetAddress,
    Intersection,
)

# address point csv from https://hub-cookcountyil.opendata.arcgis.com/datasets/5ec856ded93e4f85b3f6e1bc027a2472_0/about
address_points_path = [
    p
    for p in importlib.metadata.files("chicago_participatory_urbanism")
    if "Address_Points_reduced.csv" in str(p)
][0]
logging.info(f"Loading address points csv data from {address_points_path.locate()}")
df = pd.read_csv(address_points_path.locate())

# street center lines GeoJSON from https://data.cityofchicago.org/Transportation/Street-Center-Lines/6imu-meau
street_center_lines_path = [
    p
    for p in importlib.metadata.files("chicago_participatory_urbanism")
    if "Street Center Lines.geojson" in str(p)
][0]
logging.info(
    f"Loading street center lines csv from {street_center_lines_path.locate()}"
)
gdf = gpd.read_file(street_center_lines_path.locate())

print("Data loaded.")


class Geocoder:
    def get_street_address_coordinates_from_full_name(self, address: str):
        """
        Return the GPS coordinates of a street address in Chicago.

        Parameters:
        - address (string): A street address in Chicago matching the following format: "1763 W BELMONT AVE"

        Returns:
        - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
        """
        result = df[df["CMPADDABRV"] == address.upper()]

        try:
            longitude = result["Long"].iloc[0]
            latitude = result["Lat"].iloc[0]
        except Exception:
            (longitude, latitude) = (0, 0)

        return Point(longitude, latitude)

    def get_street_address_coordinates(
        self, address: StreetAddress, fuzziness: int = 10
    ) -> Point:
        """
        Return the GPS coordinates of a street address in Chicago.

        Parameters:
        - StreetAddress

        Returns:
        - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
        """
        results = df[
            (address.number - fuzziness <= df["Add_Number"])
            & (df["Add_Number"] <= address.number + fuzziness)
            & (df["LSt_PreDir"] == address.street.direction.upper())
            & (df["St_Name"] == address.street.name.upper())
            & (df["LSt_Type"] == address.street.street_type.upper())
        ].copy()

        # print(results[['Add_Number', 'St_Name','Long','Lat']])

        exact_address = results[results["Add_Number"] == address.number]

        try:
            if not exact_address.empty:
                # use exact address
                longitude = exact_address["Long"].iloc[0]
                latitude = exact_address["Lat"].iloc[0]
            else:
                # find closest address
                results["difference"] = abs(results["Add_Number"] - address.number)
                closest_index = results["difference"].idxmin()
                longitude = results.loc[closest_index, "Long"]
                latitude = results.loc[closest_index, "Lat"]
        except Exception:
            print(f"Error finding coordinates for street address {address}")
            return None

        return Point(longitude, latitude)

    def get_intersection_coordinates(self, intersection: Intersection) -> Point:
        """
        Return the GPS coordinates of an intersection in Chicago.

        Parameters:
        - Intersection

        Returns:
        - Point: A Shapely point with the GPS coordinates of the address (longitude, latitude).
        """
        if intersection.street1.name == intersection.street2.name:
            return None

        # select street shapes from data
        street1_data = gdf[gdf["street_nam"] == intersection.street1.name.upper()]
        street2_data = gdf[gdf["street_nam"] == intersection.street2.name.upper()]

        try:
            # join street shapes together
            street1_geometry = unary_union(street1_data["geometry"])
            street2_geometry = unary_union(street2_data["geometry"])

            intersection_geometry = street1_geometry.intersection(street2_geometry)

            if not intersection_geometry.is_empty:
                if isinstance(intersection_geometry, MultiPoint):
                    # extract first point of multipoint
                    ## (this tends to happen when one half of the intersecting street is offset from the other half)
                    first_point = intersection_geometry.geoms[0]
                    return
                if isinstance(intersection_geometry, LineString):
                    first_point = intersection_geometry.coords[0]
                    return first_point
                if isinstance(intersection_geometry, MultiLineString):
                    first_point = intersection_geometry.geoms[0].coords[0]
                    return first_point
                else:
                    return intersection_geometry
            else:
                return None
        except Exception:
            print(f"Error getting intersection coordinates for {intersection_geometry}")
            return None
