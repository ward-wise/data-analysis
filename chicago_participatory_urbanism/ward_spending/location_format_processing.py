'''
Identify location description text format and parse into
street address or street intersection
'''
import re
from enum import auto, Enum
from typing import Dict, List
import sys
from pathlib import Path
sys.path += [str(Path(__file__).resolve().parents[2])]
from location_structures import Street, StreetAddress, Intersection
from src.tests.test_cases import address_tests


class LocationFormat(Enum):
    STREET_ADDRESS = auto()
    STREET_ADDRESS_RANGE = auto()
    INTERSECTION = auto()
    STREET_SEGMENT_INTERSECTIONS = auto()
    STREET_SEGMENT_ADDRESS_INTERSECTION = auto()
    STREET_SEGMENT_INTERSECTION_ADDRESS = auto()
    ALLEY = auto()
    UNIDENTIFIED = auto()


street_suffixes = "(?:AVE|BLVD|CRES|CT|DR|ER|EXPY|HWY|LN|PKWY|PL|PLZ|RD|RL|ROW|SQ|SR|ST|TER|TOLL|WAY|XR)"
street_pattern = rf"[NWES]\s(.*)\s{street_suffixes}(?:|\s+[NWES])"
street_pattern_with_optional_suffix = rf"[NWES]\s(.*?)(?:\s{street_suffixes})?(?:|\s+[NWES])"
# special_street_names = "(?:S (AVENUE [A-Z])|N (BROADWAY)|N (LINCOLN PARK) W|W (MIDWAY PARK)|W (FULTON MARKET))"
# street_pattern = rf"(?:{street_pattern}|{special_street_names})"
# TO DO: get special street names working without breaking match.group(#) code

# TO DO: make regex robust against mistaking alley for intersection
location_patterns = {
    # Pattern for format: 1640 N MAPLEWOOD AVE
    LocationFormat.STREET_ADDRESS: rf"^\d+\s+{street_pattern}$",
    # Pattern for format: 434-442 E 46TH PL
    LocationFormat.STREET_ADDRESS_RANGE: rf"^(\d+)-(\d+)\s+({street_pattern})$",
    # Pattern for format: N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE
    # ALLEY NEEDS TO COME BEFORE INTERSECTION
    LocationFormat.ALLEY: rf"^{street_pattern_with_optional_suffix}\s*&\s*{street_pattern_with_optional_suffix}\s*&\s*{street_pattern_with_optional_suffix}\s*&\s*{street_pattern_with_optional_suffix}$",
    # Pattern for format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    LocationFormat.STREET_SEGMENT_INTERSECTIONS: rf"^ON\s+{street_pattern}\s+FROM\s+{street_pattern}\s*\(\d+\s+[NWES]\)\s*TO\s+{street_pattern}\s*\(\d+\s+[NWES]\)$",
    # Pattern for format: ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)
    LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION: rf"^ON\s+({street_pattern})\s+FROM\s+(\d+)\s+[NWES]\s+TO\s+{street_pattern}\s*\(\d+\s+[NWES]\)$",
    # Pattern for format: ON W 52ND PL FROM S PRINCETON AVE (300 W) TO 322 W
    LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS: rf"^ON\s+({street_pattern})\s+FROM\s+{street_pattern}\s*\(\d+\s+[NWES]\)\s+TO\s+(\d+)\s+[NWES]$",
    # Pattern for format: N ASHLAND AVE & W CHESTNUT ST
    LocationFormat.INTERSECTION: rf"^{street_pattern}\s*&\s*{street_pattern}$",
}


class LocationStringProcessor:

    def __init__(self, location_string: str) -> None:

        self.loc_string = str(location_string).strip()
        self.loc_string = self.loc_string.split(';')  # list of strings
        self.format = self.get_location_format(location=self.loc_string)

    def get_location_format(self, location: List[str]) -> List[Dict]:
        """
        Detect and return the address format.
        """
        address_formats = []
        for address in location:
            address = address.strip()  # watch out for extra spaces
            for format, pattern in location_patterns.items():
                if re.match(pattern, address.strip()):
                    address_formats.append(
                        {'address': address,
                         'format': format}
                    )
                    break
        return address_formats

    def run(self) -> List[Dict[LocationFormat, str]]:
        addresses = []

        for f in self.format:
            match f['format']:

                case LocationFormat.STREET_ADDRESS:
                    addresses.append(
                        {'format': f['format'],
                         'location_text_data': extract_street_address(f['address'])}
                    )

                case LocationFormat.STREET_ADDRESS_RANGE:
                    addresses.append(
                        {'format': f['format'],
                         'location_text_data': extract_address_range_street_addresses(f['address'])}
                    )

                case LocationFormat.ALLEY:
                    addresses.append(
                        {'format': f['format'],
                         'location_text_data': extract_alley_intersections(f['address'])}
                    )

                case LocationFormat.INTERSECTION:
                    addresses.append(
                        {'format': f['format'],
                         'location_text_data': extract_intersection_street_names(f['address'])}
                    )

                case LocationFormat.STREET_SEGMENT_INTERSECTIONS:
                    addresses.append(
                        {'format': f['format'],
                         'location_text_data': extract_segment_intersections(f['address'])}
                    )

                case LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION:
                    addresses.append(
                        {'format': f['format'],
                         'location_text_data': extract_segment_address_intersection_info(f['address'])}
                    )

                case LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS:
                    addresses.append(
                        {'format': f['format'],
                         'location_text_data': extract_segment_intersection_address_info(f['address'])}
                    )

                case _:
                    addresses.append(
                        {'format': f['format'],
                         'location_text_data': None}
                    )

        return addresses

    def _get_location_text_format(self, text):
        """Return a string of detected formats. Use this function to debug address format matching en masse."""

        locations = text.split(";")
        format = ""
        for location in locations:
            format += str(self.get_location_format(location)) + ";"

        return format


def extract_street_address(street_address_text: str) -> StreetAddress:
    """Return StreetAddress for the STREET_ADDRESS format."""
    address_parts = street_address_text.strip().split(" ")
    number = int(address_parts[0])
    direction = address_parts[1]
    # capture multi-word names
    name = " ".join(address_parts[2:-1])  
    street_type = address_parts[-1]

    street = Street(direction, name, street_type)
    return StreetAddress(number, street)


def extract_segment_intersections_address_range(
        location_text: str) -> tuple[StreetAddress, StreetAddress]:
    """Return location data structures for the STREET_SEGMENT_INTERSECTIONS format."""
    # Format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    pattern = r"^ON\s+([NWES]\s+\w+\s+\w+)\s+FROM\s+[NWES]\s+\w+\s+\w+\s+\((\d+)\s+[NWES]\)\s+TO\s+[NWES]\s+\w+\s+\w+\s+\((\d+)\s+[NWES]\)$"
    # Check if the address matches the pattern
    match = re.match(pattern, location_text)
    if match:
        street = match.group(1)
        start_number = match.group(2)
        end_number = match.group(3)
        # Construct the two strings in the desired format
        start_address = extract_street_address(f"{start_number} {street}")
        end_address = extract_street_address(f"{end_number} {street}")
        return start_address, end_address
    else:
        return None, None


def extract_segment_intersections(
        location_text: str) -> tuple[Intersection, Intersection]:
    """Return location data structures for the STREET_SEGMENT_INTERSECTIONS format."""
    # Format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    pattern = location_patterns[LocationFormat.STREET_SEGMENT_INTERSECTIONS]
    # Check if the address matches the pattern
    match = re.match(pattern, location_text)
    if match:
        primary_street_name = match.group(1)
        cross_street1_name = match.group(2)
        cross_street2_name = match.group(3)

        primary_street = Street(direction="", name=primary_street_name, street_type="")
        cross_street1 = Street(direction="", name=cross_street1_name, street_type="")
        cross_street2 = Street(direction="", name=cross_street2_name, street_type="")

        intersection1 = Intersection(primary_street, cross_street1)
        intersection2 = Intersection(primary_street, cross_street2)

        return (intersection1, intersection2)
    else:
        return None, None


def extract_alley_intersections(location_text: str) -> List[Intersection]:
    """Return location data structures for the ALLEY location format"""
    match = re.match(location_patterns[LocationFormat.ALLEY], location_text)

    street_name1 = match.group(1)
    street_name2 = match.group(2)
    street_name3 = match.group(3)
    street_name4 = match.group(4)

    street1 = Street(direction="", name=street_name1, street_type="")
    street2 = Street(direction="", name=street_name2, street_type="")
    street3 = Street(direction="", name=street_name3, street_type="")
    street4 = Street(direction="", name=street_name4, street_type="")

    # get every possible intersection (streets aren't in any particular order)
    intersections = []
    intersections.append(Intersection(street1, street2))
    intersections.append(Intersection(street1, street2))
    intersections.append(Intersection(street1, street3))
    intersections.append(Intersection(street1, street4))
    intersections.append(Intersection(street2, street3))
    intersections.append(Intersection(street2, street4))
    intersections.append(Intersection(street3, street4))

    return intersections


def extract_intersection_street_names(location_text: str) -> Intersection:
    """Return an Intersection for the INTERSECTION location format"""

    match = re.match(location_patterns[LocationFormat.INTERSECTION], location_text)
    street_name1 = match.group(1)
    street_name2 = match.group(2)

    street1 = Street(direction="", name=street_name1, street_type="")
    street2 = Street(direction="", name=street_name2, street_type="")
    intersection = Intersection(street1, street2)

    return intersection


def extract_address_range_street_addresses(
        location_text: str) -> tuple[StreetAddress, StreetAddress]:
    """Return location data structures for the STREET_ADDRESS_RANGE format"""
    match = re.match(location_patterns[LocationFormat.STREET_ADDRESS_RANGE], location_text)
    number1 = match.group(1)
    number2 = match.group(2)
    street = match.group(3)

    address1 = extract_street_address(f"{number1} {street}")
    address2 = extract_street_address(f"{number2} {street}")

    return (address1, address2)


def extract_segment_address_intersection_info(
        location_text: str) -> tuple[StreetAddress, Intersection]:
    """Return location data structures for the STREET_SEGMENT_ADDRESS_INTERSECTION format"""
    match = re.match(location_patterns[LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION], location_text)
    primary_street = match.group(1)
    primary_street_name = match.group(2)
    street_number = match.group(3)
    cross_street_name = match.group(4)

    street1 = Street(direction="", name=primary_street_name, street_type="")
    street2 = Street(direction="", name=cross_street_name, street_type="")
    intersection = Intersection(street1, street2)

    address = extract_street_address(f"{street_number} {primary_street}")

    return (address, intersection)


def extract_segment_intersection_address_info(
        location_text: str) -> tuple[Intersection, StreetAddress]:
    """Return location data structures for the STREET_SEGMENT_INTERSECTION_ADDRESS format"""
    match = re.match(location_patterns[LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS], location_text)
    primary_street = match.group(1)
    primary_street_name = match.group(2)
    cross_street_name = match.group(3)
    street_number = match.group(4)

    street1 = Street(direction="", name=primary_street_name, street_type="")
    street2 = Street(direction="", name=cross_street_name, street_type="")
    intersection = Intersection(street1, street2)

    address = extract_street_address(f"{street_number} {primary_street}")

    return (intersection, address)


def get_location_format(location):
    """Detect and return the address format."""
    for format, pattern in location_patterns.items():
        if re.match(pattern, location.strip()):
            return format

    return None


# TODO implement unittest and move this code to test specific files
if __name__ == '__main__':
    
    # for test in address_tests()[:4]:
    #     print('---'*25)
    #     print(test)
    #     print(LocationStringProcessor(location_string=test).run())
    loc_1 = 'N MILWAUKEE AVE & N WASHTENAW AVE'
    print(get_location_format(loc_1))
    print(extract_intersection_street_names(loc_1).street1)