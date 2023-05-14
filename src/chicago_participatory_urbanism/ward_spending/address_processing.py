import re
from enum import auto,Enum

class AddressFormat(Enum):
    STREET_ADDRESS = auto()
    STREET_ADDRESS_RANGE = auto()
    INTERSECTION = auto()
    STREET_SEGMENT_INTERSECTIONS = auto()
    STREET_SEGMENT_ADDRESS_INTERSECTION = auto()
    STREET_SEGMENT_INTERSECTION_ADDRESS = auto()
    ALLEY = auto()


# TO DO: modify regex to work with two word street names (e.g., COTTAGE GROVE)
address_patterns = {
    # Pattern for format: 1640 N MAPLEWOOD AVE
    AddressFormat.STREET_ADDRESS: r"^\d+\s+[NWES]\s+\w+\s+\w+$",
    # Pattern for format: 434-442 E 46TH PL
    AddressFormat.STREET_ADDRESS_RANGE: r"^\d+-\d+\s+[NWES]\s+\w+\s+\w+$",
    # Pattern for format: N ASHLAND AVE & W CHESTNUT ST
    AddressFormat.INTERSECTION: r"^[NWES]\s+\w+\s+\w+\s+&\s+[NWES]+\s+\w+\s+\w+$",
    # Pattern for format: N WOOD ST & W AUGUSTA BLVD & W CORTEZ ST & N HERMITAGE AVE
    AddressFormat.ALLEY: r"^[NWES]\s+\w+\s+\w+\s+&\s+[NWES]\s+\w+\s+\w+\s+&\s+[NWES]\s+\w+\s+\w+\s+&\s+[NWES]\s+\w+\s+\w+$",
    # Pattern for format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    AddressFormat.STREET_SEGMENT_INTERSECTIONS: r"^ON\s+([NWES]\s+\w+\s+\w+)\s+FROM\s+[NWES]\s+\w+\s+\w+\s+\((\d+)\s+[NWES]\)\s+TO\s+[NWES]\s+\w+\s+\w+\s+\((\d+)\s+[NWES]\)$",
    # Pattern for format: ON W 52ND PL FROM 322 W TO S PRINCETON AVE (300 W)
    AddressFormat.STREET_SEGMENT_ADDRESS_INTERSECTION: r"^ON\s+[NWES]\s+\w+\s+\w+\s+FROM\s+\d+\s+[NWES]\s+TO\s+[NWES]\s+\w+\s+\w+\s+\(\d+\s+[NWES]\)$",
    # Pattern for format: ON W 52ND PL FROM S PRINCETON AVE (300 W) TO 322 W
    AddressFormat.STREET_SEGMENT_INTERSECTION_ADDRESS: r"^ON\s+[NWES]\s+\w+\s+\w+\s+FROM\s+[NWES]\s+\w+\s+\w+\s+\(\d+\s+[NWES]\)\s+TO\s+\d+\s+[NWES]$",
}

def get_address_format(address):
    """Detect and return the address format."""
    for format, pattern in address_patterns.items():
        if re.match(pattern, address):
            return format

    return None


def extract_address_range(address):
    """For the STREET_SEGMENT_INTERSECTIONS format, return a tuple with the address of the first and second intersection"""
    # Format: ON N LEAVITT ST FROM W DIVISION ST (1200 N) TO W NORTH AVE (1600 N)
    pattern = address_patterns[AddressFormat.STREET_SEGMENT_INTERSECTIONS]
    # Check if the address matches the pattern
    match = re.match(pattern, address)
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
