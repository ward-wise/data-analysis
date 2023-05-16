import re
from shapely.geometry import Point, MultiPoint, LineString
from enum import auto, Enum
import chicago_participatory_urbanism.geocoder as geocoder


class LocationFormat(Enum):
    STREET_ADDRESS = auto()
    STREET_ADDRESS_RANGE = auto()
    INTERSECTION = auto()
    STREET_SEGMENT_INTERSECTIONS = auto()
    STREET_SEGMENT_ADDRESS_INTERSECTION = auto()
    STREET_SEGMENT_INTERSECTION_ADDRESS = auto()
    ALLEY = auto()


# TO DO: modify regex to work with two word street names (e.g., COTTAGE GROVE)
location_patterns = {
    # Pattern for format: 1640 N MAPLEWOOD AVE
    LocationFormat.STREET_ADDRESS: r"^\d+\s+[NWES]\s+\w+\s+\w+$",
    # Pattern for format: 434-442 E 46TH PL
    LocationFormat.STREET_ADDRESS_RANGE: r"^(\d+)-(\d+)\s+([NWES]\s+\w+\s+\w+)$",
    # Pattern for format: N ASHLAND AVE & W CHESTNUT ST
    LocationFormat.INTERSECTION: r"^[NWES]\s+(\w+)\s+\w+\s+&\s+[NWES]+\s+(\w+)\s+\w+$",
    # Pattern for format: N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE
    LocationFormat.ALLEY: r"^[NWES]\s+\w+\s+\w+\s*&\s*[NWES]\s+\w+\s+\w+\s*&\s*[NWES]\s+\w+\s+\w+\s*&\s*[NWES]\s+\w+\s+\w+$",
    # Pattern for format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    LocationFormat.STREET_SEGMENT_INTERSECTIONS: r"^ON\s+([NWES]\s+\w+\s+\w+)\s+FROM\s+[NWES]\s+\w+\s+\w+\s+\((\d+)\s+[NWES]\)\s+TO\s+[NWES]\s+\w+\s+\w+\s+\((\d+)\s+[NWES]\)$",
    # Pattern for format: ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)
    LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION: r"^ON\s+[NWES]\s+\w+\s+\w+\s+FROM\s+\d+\s+[NWES]\s+TO\s+[NWES]\s+\w+\s+\w+\s+\(\d+\s+[NWES]\)$",
    # Pattern for format: ON W 52ND PL FROM S PRINCETON AVE (300 W) TO 322 W
    LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS: r"^ON\s+[NWES]\s+\w+\s+\w+\s+FROM\s+[NWES]\s+\w+\s+\w+\s+\(\d+\s+[NWES]\)\s+TO\s+\d+\s+[NWES]$",
}


def get_location_format(location):
    """Detect and return the address format."""
    for format, pattern in location_patterns.items():
        if re.match(pattern, location.strip()):
            return format

    return None


def extract_address_range(street_segment_intersections):
    """For the STREET_SEGMENT_INTERSECTIONS format, return a tuple with the address of the first and second intersection"""
    # Format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    pattern = location_patterns[LocationFormat.STREET_SEGMENT_INTERSECTIONS]
    # Check if the address matches the pattern
    match = re.match(pattern, street_segment_intersections)
    if match:
        street = match.group(1)
        start_number = match.group(2)
        end_number = match.group(3)
        # Construct the two strings in the desired format
        start_address = f"{start_number} {street}"
        end_address = f"{end_number} {street}"
        return start_address, end_address
    else:
        return None, None


def get_location_text_format(text):
    """Return a string of detected formats. Use this function to debug address format matching en masse."""

    locations = text.split(";")
    format = ""
    for location in locations:
        format += str(get_location_format(location)) + ";"

    return format


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
    format = get_location_format(location)
    match format:
        case LocationFormat.STREET_ADDRESS:
            return get_geometry_from_street_address(location)

        case LocationFormat.STREET_ADDRESS_RANGE:
            match = re.match(location_patterns[LocationFormat.STREET_ADDRESS_RANGE], location)
            number1 = match.group(1)
            number2 = match.group(2)
            street = match.group(3)

            address1 = f"{number1} {street}"
            address2 = f"{number2} {street}"
            point1 = get_geometry_from_street_address(address1)
            point2 = get_geometry_from_street_address(address2)
            street_segment = LineString([point1, point2])
            return street_segment

        case LocationFormat.INTERSECTION:
            match = re.match(location_patterns[LocationFormat.INTERSECTION], location)
            street1 = match.group(1)
            street2 = match.group(2)
            intersection = geocoder.get_intersection_coordinates(street1, street2)
            return intersection

        case LocationFormat.STREET_SEGMENT_INTERSECTIONS:
            # TO DO change to use intersection function instead of street address
            (street_address1, street_address2) = extract_address_range(location)
            point1 = get_geometry_from_street_address(street_address1)
            point2 = get_geometry_from_street_address(street_address2)
            street_segment = LineString([point1, point2])
            return street_segment

        case LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION:
            #handle_street_segment_address_intersection()
            return None

        case LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS:
            #handle_street_segment_intersection_address()
            return None

        case LocationFormat.ALLEY:
            #handle_alley()
            return None

        case _ :
            return None


def get_geometry_from_street_address(street_address):
    address_parts = street_address.strip().split(" ")
    number = int(address_parts[0])
    direction = address_parts[1]
    name = " ".join(address_parts[2:-1]) #capture multi-word names
    street_type = address_parts [-1]
    geometry = geocoder.get_street_address_coordinates(number, direction, name, street_type)
    return geometry
