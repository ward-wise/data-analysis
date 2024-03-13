from dataclasses import dataclass, field


@dataclass
class Street:
    name: str
    direction: str = field(compare=False)
    street_type: str = field(compare=False)

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
