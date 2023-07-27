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
                feature_type = feature['geometry']['type']
                properties = feature['properties']
                if feature_type == 'Point':
                    coordinates = extract_point_coordinates(feature)
                    row_data = {'latitude': coordinates[1], 'longitude': coordinates[0]}
                    row_data.update(properties)
                    writer.writerow(row_data)
                # elif feature_type == 'MultiPoint':
                    # divide cost equally among points
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
            except Exception as e:
                print(e)

def extract_point_coordinates(feature):
    geometry = feature['geometry']
    if geometry['type'] == 'Point':
        return geometry['coordinates']
    return None

if __name__ == "__main__":

    import os
    input_geojson_path = os.path.join(os.getcwd(), "data", "2019-2022 data_geocoded.geojson")
    output_csv_path = os.path.join(os.getcwd(), "data","output","2019-2022 ward spending heatmap data.csv")
    print(input_geojson_path)

    with open(input_geojson_path, 'r') as geojson_file:
        data = json.load(geojson_file)
            
    export_to_heatmap_csv(data, output_csv_path)

