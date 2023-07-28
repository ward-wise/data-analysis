import json
import csv

def export_to_heatmap_csv(geojson_data, output_csv_path):
    """Convert geojson data into points for use in heatmapping."""

    if geojson_data['type'] != 'FeatureCollection':
        raise ValueError("Invalid GeoJSON format. The input file should be a FeatureCollection.")

    with open(output_csv_path, 'w', newline='') as csv_file:
        fieldnames = ['latitude', 'longitude'] + list(geojson_data["features"][0]['properties'].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for feature in geojson_data["features"]:
            try:
                geometry = feature['geometry']
                feature_type = geometry['type']
                properties = feature['properties']
                cost = properties["cost"]
                properties.pop("cost") # remove cost from properties

                if feature_type == 'Point':
                    points = [geometry['coordinates']]
                    cost_per_point = cost
                elif feature_type == 'MultiPoint':
                    (points, cost_per_point) = split_cost_for_multipoint(geometry, cost)
                # elif feature_type == 'LineString':
                    # generate a line of points with costs equally divided
                # elif feature_type == 'MultiLineString':
                    # split costs across linestrings based on length
                # elif feature_type == 'Polygon':
                    # generate a cloud of points with costs equally divided
                # elif feature_type == 'GeometryCollection':

                else:
                    # Note: MultiPolygons not present in original dataset
                    raise ValueError(f"Unsupported geometry type {feature_type} for {properties}")
                
                for coordinates in points:
                    row_data = {'latitude': coordinates[1], 'longitude': coordinates[0]}
                    row_data.update(properties)
                    row_data.update( {'cost': cost_per_point})
                    writer.writerow(row_data)
            except Exception as e:
                print(e)


def split_cost_for_multipoint(geometry, combined_cost):
    if geometry['type'] != 'MultiPoint':
        raise ValueError("Invalid MultiPoint feature.")

    combined_cost = float(combined_cost)
    points = geometry['coordinates']

    total_points = len(geometry['coordinates'])
    if total_points == 0:
        raise ValueError("MultiPoint feature contains no points.")

    if combined_cost < 0:
        raise ValueError("Cost per point should be a positive value.")

    cost_per_point = combined_cost / total_points
    return (points, cost_per_point)


if __name__ == "__main__":

    import os
    input_geojson_path = os.path.join(os.getcwd(), "data", "2019-2022 data_geocoded.geojson")
    output_csv_path = os.path.join(os.getcwd(), "data","output","2019-2022 ward spending heatmap data.csv")
    print(input_geojson_path)

    with open(input_geojson_path, 'r') as geojson_file:
        data = json.load(geojson_file)
            
    export_to_heatmap_csv(data, output_csv_path)

