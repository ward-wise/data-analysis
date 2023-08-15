'''
This section is to break down loacation description text in
ward spend PDF report
'''
import re
from enum import auto, Enum
from typing import Dict


class LocationFormat(Enum):
    STREET_ADDRESS = auto()
    STREET_ADDRESS_RANGE = auto()
    INTERSECTION = auto()
    STREET_SEGMENT_INTERSECTIONS = auto()
    STREET_SEGMENT_ADDRESS_INTERSECTION = auto()
    STREET_SEGMENT_INTERSECTION_ADDRESS = auto()
    ALLEY = auto()
    UNIDENTIFY = auto()


street_suffixes = "(?:AVE|BLVD|CRES|CT|DR|ER|EXPY|HWY|LN|PKWY|PL|PLZ|RD|RL|ROW|SQ|SR|ST|TER|TOLL|WAY|XR)"
street_pattern = rf"[NWES]\s(.*)\s{street_suffixes}(?:|\s+[NWES])"
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
    LocationFormat.ALLEY: rf"^{street_pattern}\s*&\s*{street_pattern}\s*&\s*{street_pattern}\s*&\s*{street_pattern}$",
    # Pattern for format: N ASHLAND AVE & W CHESTNUT ST
    LocationFormat.INTERSECTION: rf"^{street_pattern}\s*&\s*{street_pattern}$",
    # Pattern for format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    LocationFormat.STREET_SEGMENT_INTERSECTIONS: rf"^ON\s+{street_pattern}\s+FROM\s+{street_pattern}\s*\(\d+\s+[NWES]\)\s*TO\s+{street_pattern}\s*\(\d+\s+[NWES]\)$",
    # Pattern for format: ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)
    LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION: rf"^ON\s+({street_pattern})\s+FROM\s+(\d+)\s+[NWES]\s+TO\s+{street_pattern}\s*\(\d+\s+[NWES]\)$",
    # Pattern for format: ON W 52ND PL FROM S PRINCETON AVE (300 W) TO 322 W
    LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS: rf"^ON\s+({street_pattern})\s+FROM\s+{street_pattern}\s*\(\d+\s+[NWES]\)\s+TO\s+(\d+)\s+[NWES]$",
}


class LocationStringProcessor:

    def __init__(self, location_string: str) -> None:

        self.loc_string = str(location_string).strip()
        self.format = self.get_location_format(location=self.loc_string)

    def get_location_format(self, location) -> 'LocationFormat':
        """Detect and return the address format."""
        for format, pattern in location_patterns.items():
            if re.match(pattern, location.strip()):
                return format
        return LocationFormat.UNIDENTIFY

    def run(self) -> Dict[LocationFormat, str]:
        match self.format:
            case LocationFormat.STREET_ADDRESS:
                return {'format': self.format,
                        'proc_string': self.loc_string}

            case LocationFormat.STREET_ADDRESS_RANGE:
                return {
                    'format': self.format,
                    'proc_string': extract_address_range_street_addresses(self.loc_string)
                }

            case LocationFormat.ALLEY:
                return {
                    'format': self.format,
                    'proc_string': extract_alley_street_names(self.loc_string)
                }

            case LocationFormat.INTERSECTION:
                return {
                    'format': self.format,
                    'proc_string': extract_intersection_street_names(self.loc_string)
                }

            case LocationFormat.STREET_SEGMENT_INTERSECTIONS:
                return {
                    'format': self.format,
                    'proc_string': extract_segment_intersections_street_names(self.loc_string)
                }

            case LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION:
                return {
                    'format': self.format,
                    'proc_string': extract_segment_address_intersection_info(self.loc_string)
                }

            case LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS:
                return {
                    'format': self.format,
                    'proc_string': extract_segment_intersection_address_info(self.loc_string)
                }

            case _:
                return {
                    'format': self.format,
                    'proc_string': None
                }


def extract_street_name_and_number(street_string):
    street_string = street_string.strip()
    pattern = location_patterns[LocationFormat.STREET_ADDRESS]
    match = re.match(pattern, street_string)
    print(match)
    if match:
        add_num = match.group(0)
        return add_num

    return None, None


def extract_segment_intersections_address_range(street_segment_intersections):
    """For the STREET_SEGMENT_INTERSECTIONS format, return a tuple with the address of the first and second intersection"""
    # Format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    pattern = r"^ON\s+([NWES]\s+\w+\s+\w+)\s+FROM\s+[NWES]\s+\w+\s+\w+\s+\((\d+)\s+[NWES]\)\s+TO\s+[NWES]\s+\w+\s+\w+\s+\((\d+)\s+[NWES]\)$"
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


def extract_segment_intersections_street_names(street_segment_intersections):
    """For the STREET_SEGMENT_INTERSECTIONS format, return a tuple with the primary street and two cross streets."""
    # Format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    pattern = location_patterns[LocationFormat.STREET_SEGMENT_INTERSECTIONS]
    # Check if the address matches the pattern
    match = re.match(pattern, street_segment_intersections)
    if match:
        primary_street = match.group(1)
        cross_street1 = match.group(2)
        cross_street2 = match.group(3)
        return (primary_street, cross_street1, cross_street2)
    else:
        return None, None, None


def get_location_text_format(text):
    """Return a string of detected formats. Use this function to debug address format matching en masse."""

    locations = text.split(";")
    format = ""
    for location in locations:
        format += str(get_location_format(location)) + ";"

    return format


def extract_alley_street_names(location):
    """Return a tuple of 4 street names for the ALLEY location format"""

    match = re.match(location_patterns[LocationFormat.ALLEY], location)
    street1 = match.group(1)
    street2 = match.group(2)
    street3 = match.group(3)
    street4 = match.group(4)

    return (street1, street2, street3, street4)


def extract_intersection_street_names(location):
    """Return a tuple of 2 street names for the INTERSECTION location format"""

    match = re.match(location_patterns[LocationFormat.INTERSECTION], location)
    street1 = match.group(1)
    street2 = match.group(2)

    return (street1, street2)


def extract_address_range_street_addresses(location):
    """Return a tuple of 2 street addresses for the STREET_ADDRESS_RANGE format"""
    match = re.match(location_patterns[LocationFormat.STREET_ADDRESS_RANGE], location)
    number1 = match.group(1)
    number2 = match.group(2)
    street = match.group(3)

    address1 = f"{number1} {street}"
    address2 = f"{number2} {street}"

    return (address1, address2)


def extract_segment_address_intersection_info(location):
    """Return a tuple of a street address and 2 street names for the STREET_SEGMENT_ADDRESS_INTERSECTION format"""
    match = re.match(location_patterns[LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION], location)
    primary_street = match.group(1)
    primary_street_name = match.group(2)
    street_number = match.group(3)
    cross_street_name = match.group(4)
    address = f"{street_number} {primary_street}"

    return (address, primary_street_name, cross_street_name)


def extract_segment_intersection_address_info(location):
    """Return a tuple of 2 street names and a street address for the STREET_SEGMENT_INTERSECTION_ADDRESS format"""
    match = re.match(location_patterns[LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS], location)
    primary_street = match.group(1)
    primary_street_name = match.group(2)
    cross_street_name = match.group(3)
    street_number = match.group(4)
    address = f"{street_number} {primary_street}"

    return (primary_street_name, cross_street_name, address)


if __name__ == '__main__':
    loc_1 = '6754 S EUCLID AVE; ON W 68TH ST FROM S BENNETT AVE  (1900 E) TO S EUCLID AVE  (1930 E)'
    print(extract_street_name_and_number(loc_1))
    print(LocationStringProcessor(location_string=loc_1).run())
