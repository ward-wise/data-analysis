import json
import csv
import math
from math import radians, sin, cos, sqrt, atan2

# determins how many points to split lines and polygons into
POINT_RESOLUTION_DISTANCE = 0.010  # km


def export_to_heatmap_csv(geojson_data, output_csv_path):
    """Convert geojson data into points for use in heatmapping."""

    if geojson_data['type'] != 'FeatureCollection':
        raise ValueError(
            "Invalid GeoJSON format. The input file should be a FeatureCollection.")

    with open(output_csv_path, 'w', newline='') as csv_file:
        fieldnames = ['latitude', 'longitude'] + \
            list(geojson_data["features"][0]['properties'].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for feature in geojson_data["features"]:
            try:
                geometry = feature['geometry']
                feature_type = geometry['type']
                properties = feature['properties']
                combined_cost = properties["cost"]
                properties.pop("cost")  # remove cost from properties

                if feature_type == 'Point':
                    points = [geometry['coordinates']]
                elif feature_type == 'MultiPoint':
                    points = geometry['coordinates']
                elif feature_type == 'LineString':
                    # generate a line of points with costs equally divided
                    points = interpolate_points_from_line_string(geometry)
                # elif feature_type == 'MultiLineString':
                    # split costs across linestrings based on length
                # elif feature_type == 'Polygon':
                    # generate a cloud of points with costs equally divided
                # elif feature_type == 'GeometryCollection':

                else:
                    # Note: MultiPolygons not present in original dataset
                    raise ValueError(f"Unsupported geometry type {feature_type}.")

                combined_cost = float(combined_cost)
                cost_per_point = combined_cost / len(points)
                for coordinates in points:
                    row_data = {'latitude': coordinates[1], 'longitude': coordinates[0]}
                    row_data.update(properties)
                    row_data.update({'cost': cost_per_point})
                    writer.writerow(row_data)
            except Exception as e:
                print(f"{e} {properties}")


def interpolate_points_from_line_string(geometry):
    if geometry['type'] != 'LineString':
        raise ValueError("Invalid LineString feature.")

    line_points = geometry['coordinates']
    if len(line_points) == 0:
        raise ValueError("LineString feature contains no points.")
    if len(line_points) == 1:
        raise ValueError("LineString feature contains only one point.")
    if len(line_points) > 2:
        # temporary
        raise ValueError("Function cannot handle LineString feature with more than two points.")

    line_length = get_line_length(geometry)
    num_of_interpolated_points = math.ceil(line_length/POINT_RESOLUTION_DISTANCE)
    if num_of_interpolated_points == 1:
        num_of_interpolated_points = 2
    points = linear_interpolation(line_points[0], line_points[1], num_of_interpolated_points)

    # TODO handle lines with multiple segments

    return points


def haversine_distance(coord1, coord2):
    # Approximate radius of Earth in km
    R = 6371.0

    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def get_line_length(geometry):
    if geometry['type'] != 'LineString':
        raise ValueError("Invalid LineString feature.")

    coordinates = geometry['coordinates']
    length = 0

    for i in range(1, len(coordinates)):
        length += haversine_distance(coordinates[i - 1], coordinates[i])

    return length


def linear_interpolation(start_point, end_point, num_points):
    """ Returns an array of points between and including the start and end points.
    
    num_points = total of number of points to return in the array, including the start and end point
    """
    x0, y0 = start_point
    x1, y1 = end_point

    if num_points < 2:
        raise ValueError(f"Number of points ({num_points}) should be at least 2.")

    interpolated_points = []

    for i in range(num_points):
        ratio = i / (num_points - 1)
        x = x0 + (x1 - x0) * ratio
        y = y0 + (y1 - y0) * ratio
        interpolated_points.append((x, y))

    return interpolated_points


if __name__ == "__main__":

    import os
    input_geojson_path = os.path.join(os.getcwd(), "data", "2019-2022 data_geocoded.geojson")
    output_csv_path = os.path.join(os.getcwd(), "data", "output", "2019-2022 ward spending heatmap data.csv")
    print(input_geojson_path)

    with open(input_geojson_path, 'r') as geojson_file:
        data = json.load(geojson_file)

    export_to_heatmap_csv(data, output_csv_path)