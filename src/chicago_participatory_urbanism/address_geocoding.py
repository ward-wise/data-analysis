from shapely.geometry import Point, MultiPoint, LineString, Polygon
import math
import geocoder as geocoder
import address_format_processing as afp


def process_location_text(text: str):
    """Take the location text from the ward spending data and return a geometry matching the GPS coordinates."""

    locations = text.split(";")

    geometry = None
    try:
        for location in locations:
            location_geometry = get_geometry_from_location(location)
            # assign if geometry is empty, otherwise add to existing geometry
            if geometry is None:
                geometry = location_geometry
            else:
                geometry = geometry.union(location_geometry)

        return geometry
    
    except Exception as e:
        print(f"Full location text: {text}")
        print(f"An error occurred: {str(e)}\n")
        return None



def get_geometry_from_location(location):
    location = location.strip() #remove whitespace
    format = afp.get_location_format(location)
    try:
        match format:
            case afp.LocationFormat.STREET_ADDRESS:
                return get_geometry_from_street_address(location)

            case afp.LocationFormat.STREET_ADDRESS_RANGE:
                (address1, address2) =afp.extract_address_range_street_addresses(location)
                point1 = get_geometry_from_street_address(address1)
                point2 = get_geometry_from_street_address(address2)
                street_segment = LineString([point1, point2])
                return street_segment

            case afp.LocationFormat.INTERSECTION:
                (street1, street2) = afp.extract_intersection_street_names(location)
                intersection = geocoder.get_intersection_coordinates(street1, street2)
                return intersection

            case afp.LocationFormat.STREET_SEGMENT_INTERSECTIONS:
                (primary_street, cross_street1, cross_street2) = afp.extract_segment_intersections_street_names(location)
                point1 = geocoder.get_intersection_coordinates(primary_street, cross_street1)
                point2 = geocoder.get_intersection_coordinates(primary_street, cross_street2)
                street_segment = LineString([point1, point2])
                return street_segment

            case afp.LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION:
                (address, primary_street, cross_street) = afp.extract_segment_address_intersection_info(location)
                point1 = geocoder.get_intersection_coordinates(primary_street, cross_street)
                point2 = get_geometry_from_street_address(address)
                street_segment = LineString([point1, point2])
                return street_segment

            case afp.LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS:
                (primary_street, cross_street, address) = afp.extract_segment_intersection_address_info(location)
                point1 = geocoder.get_intersection_coordinates(primary_street, cross_street)
                point2 = get_geometry_from_street_address(address)
                street_segment = LineString([point1, point2])
                return street_segment

            case afp.LocationFormat.ALLEY:
                (street1, street2, street3, street4) = afp.extract_alley_street_names(location)
                points = []

                # get every possible intersection of points (streets aren't in any particular order)
                points.append(geocoder.get_intersection_coordinates(street1, street2))
                points.append(geocoder.get_intersection_coordinates(street1, street3))
                points.append(geocoder.get_intersection_coordinates(street1, street4))
                points.append(geocoder.get_intersection_coordinates(street2, street3))
                points.append(geocoder.get_intersection_coordinates(street2, street4))
                points.append(geocoder.get_intersection_coordinates(street3, street4))

                # remove None values from the array and place points in clockwise order
                points = [point for point in points if point is not None]
                points = get_clockwise_sequence(points)
            
                coordinates = [(point.x, point.y) for point in points]
                alley_bounding_box = box = Polygon(coordinates)
                return alley_bounding_box

            case _ :
                print(f"Location text: {location}")
                print(f"No format match found.\n")
                return None
            
    except Exception as e:
        print(f"Location text: {location}")
        print(f"An error occurred: {str(e)}\n")
        return None


def get_geometry_from_street_address(street_address):
    address_parts = street_address.strip().split(" ")
    number = int(address_parts[0])
    direction = address_parts[1]
    name = " ".join(address_parts[2:-1]) #capture multi-word names
    street_type = address_parts [-1]
    geometry = geocoder.get_street_address_coordinates(number, direction, name, street_type, 20)
    return geometry

def get_clockwise_sequence(points):
    centroid = Point(sum(point.x for point in points) / len(points), sum(point.y for point in points) / len(points))

    angles = []
    for point in points:
        dx = point.x - centroid.x
        dy = point.y - centroid.y
        angle = math.atan2(dy, dx)
        angles.append(angle)

    sorted_points = [p for _, p in sorted(zip(angles, points))]

    return sorted_points


if __name__ == '__main__':
    loc_text = 'W FULLERTON AVE &  N WESTERN AVE&N ARTESIAN AVE &  W ALTGELD ST; 2440 N WESTERN AVE'
    
    process_location_text(text=loc_text)