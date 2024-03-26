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

    def __eq__(self, other):
        return (self.street1 == other.street1 and self.street2 == other.street2) or (
            self.street1 == other.street2 and self.street2 == other.street1
        )


@dataclass
class StreetAddress:
    number: int
    street: Street

    def __str__(self):
        return f"{self.number} {self.street}"
