from shapely.geometry import Point, MultiPoint, LineString, Polygon
import re
import chicago_participatory_urbanism.geocoder as geocoder
import chicago_participatory_urbanism.ward_spending.address_format_processing as afp


def process_location_text(text):
    """Take the location text from the ward spending data and return a geometry matching the GPS coordinates."""

    locations = text.split(";")

    geometry = None
    for location in locations:
        location_geometry = get_geometry_from_location(location)
        # assign if geometry is empty, otherwise add to existing geometry
        if geometry is None:
            geometry = location_geometry
        else:
            geometry = geometry.union(location_geometry)

    return geometry



def get_geometry_from_location(location):
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
                #handle_street_segment_address_intersection()
                return None

            case afp.LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS:
                #handle_street_segment_intersection_address()
                return None

            case afp.LocationFormat.ALLEY:
                (street1, street2, street3, street4) = afp.extract_alley_street_names(location)
                point1 = geocoder.get_intersection_coordinates(street1, street2)
                point2 = geocoder.get_intersection_coordinates(street2, street3)
                point3 = geocoder.get_intersection_coordinates(street3, street4)
                point4 = geocoder.get_intersection_coordinates(street4, street1)
                alley_bounding_box = box = Polygon([point1, point2, point3, point4])
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