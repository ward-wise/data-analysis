from dataclasses import dataclass


@dataclass
class Street:
    direction: str
    name: str
    street_type: str

    def __str__(self):
        return f"{self.direction} {self.name} {self.street_type}"


@dataclass
class Intersection:
    street1: Street
    street2: Street

    def __str__(self):
        return f"{self.street1} & {self.street2}"


@dataclass
class StreetAddress:
    number: int
    street: Street

    def __str__(self):
        return f"{self.number} {self.street}"
