import json
import csv
import random
import math
from math import radians, sin, cos, sqrt, atan2
from shapely.geometry import Point, Polygon, shape

# determins how many points to split lines and polygons into
POINT_RESOLUTION_DISTANCE = 0.050  # km


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
                properties = feature['properties']
                combined_cost = properties["cost"]
                properties.pop("cost")  # remove cost from properties

                if geometry == None:
                    continue # TODO remove after testing
                    raise ValueError("Feature is missing geometry.")

                # generate heatmap points and calculate cost per point
                points = interpolate_points_from_geometry(geometry)
                cost_per_point = float(combined_cost) / len(points)

                for coordinates in points:
                    row_data = {'latitude': coordinates[1], 'longitude': coordinates[0]}
                    row_data.update(properties)
                    row_data.update({'cost': cost_per_point})
                    writer.writerow(row_data)
            except Exception as e:
                print(f"{e} {properties}")


# point interpolation functions

def interpolate_points_from_geometry(geometry):
    
    feature_type = geometry['type']

    if feature_type == 'Point':
        points = [geometry['coordinates']]
    elif feature_type == 'MultiPoint':
        points = geometry['coordinates']
    elif feature_type == 'LineString':
        points = interpolate_points_from_line_string(geometry)
    elif feature_type == 'MultiLineString':
        points = interpolate_points_from_multi_line_string(geometry)
    elif feature_type == 'Polygon':
        points = interpolate_points_from_polygon(geometry)
    elif feature_type == 'GeometryCollection':
        points = []
        for inner_geometry in geometry['geometries']:
            #recursive call
            points += interpolate_points_from_geometry(inner_geometry)
    else:
        # Note: MultiPolygons not present in original dataset
        raise ValueError(f"Unsupported geometry type {feature_type}.")
        
    return points


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

    # TODO handle lines with multiple segments. Low priority; none of the data has multiple segments

    return points


def interpolate_points_from_multi_line_string(geometry):
    points = []
    for line_coordinates in geometry['coordinates']:
        # create line feature to maintain function compatability
        line_feature = {"type": "LineString", "coordinates":line_coordinates}

        points += interpolate_points_from_line_string(line_feature)

    return points


def interpolate_points_from_polygon(geometry):
    '''Return centroid of polygon (temporary implementation)'''
    # TODO return point cloud
    polygon = shape(geometry)
    centroid = polygon.centroid
    points = [[centroid.x, centroid.y]]
    return points

# helper functions

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
        interpolated_points.append([x, y])

    return interpolated_points

def linear_interpolation_by_distance(distance_along_line, data_points):
    """Not implemented yet. Use to interpolate a point by distance on a multi-segment line."""
    # TODO test and implement. Low priority; for use in multi-segment linestrings
    total_distance = 0.0
    for i in range(len(data_points) - 1):
        x1, y1 = data_points[i]
        x2, y2 = data_points[i + 1]
        segment_distance = haversine_distance((x1, y1), (x2, y2))
        total_distance += segment_distance
        if total_distance >= distance_along_line:
            remaining_distance = total_distance - distance_along_line
            x = x2 - remaining_distance * (x2 - x1) / segment_distance
            y = y2 - remaining_distance * (y2 - y1) / segment_distance
            return (x,y)

    # If distance_along_line is beyond the last point, return the last point's coordinates.
    return data_points[-1]


def generate_points_in_polygon(polygon_points, max_distance):
    polygon = Polygon(polygon_points)
    min_distance = max_distance / (2**0.5)  # Minimum distance between points

    def is_valid_point(point):
        return polygon.contains(Point(point)) and all(
            Point(p).distance(Point(point)) >= min_distance for p in sample_points
        )

    sample_points = []
    active_points = []

    def add_point(point):
        active_points.append(point)
        sample_points.append(point)

    # Choose a random point inside the polygon to start
    start_x = random.uniform(min(polygon_points, key=lambda p: p[0])[0],
                             max(polygon_points, key=lambda p: p[0])[0])
    start_y = random.uniform(min(polygon_points, key=lambda p: p[1])[1],
                             max(polygon_points, key=lambda p: p[1])[1])

    add_point((start_x, start_y))

    while active_points:
        random_index = random.randint(0, len(active_points) - 1)
        active_point = active_points[random_index]

        found_new_point = False
        for _ in range(30):  # Try a maximum of 30 candidate points for each active point
            angle = random.uniform(0, 2 * 3.141592653589793)  # Random angle in radians
            distance = random.uniform(min_distance, 2 * min_distance)
            new_x = active_point[0] + distance * math.cos(angle)
            new_y = active_point[1] + distance * math.sin(angle)
            new_point = (new_x, new_y)

            if is_valid_point(new_point):
                add_point(new_point)
                found_new_point = True
                break

        if not found_new_point:
            active_points.pop(random_index)

    return sample_points






if __name__ == "__main__":

    import os
    input_geojson_path = os.path.join(os.getcwd(), "data", "2019-2022 data_geocoded.geojson")
    output_csv_path = os.path.join(os.getcwd(), "data", "output", "2019-2022 ward spending heatmap data.csv")
    print(input_geojson_path)

    with open(input_geojson_path, 'r') as geojson_file:
        data = json.load(geojson_file)

    export_to_heatmap_csv(data, output_csv_path)