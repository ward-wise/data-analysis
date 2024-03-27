from shapely.geometry import Point, LineString, Polygon
import math
import src.chicago_participatory_urbanism.ward_spending.location_format_processing as lfp

class LocationGeocoder:

    def __init__(self, geocoder):
        self.geocoder = geocoder

    def process_location_text(self, text):
        """
        Take the location text from the ward spending data and
        return a geometry matching the GPS coordinates.
        """

        locations = text.split(";")

        geometry = None

        for location in locations:
            location_geometry = self.get_geometry_from_location(location)
            # assign if geometry is empty, otherwise add to existing geometry
            if geometry is None:
                geometry = location_geometry
            else:
                geometry = geometry.union(location_geometry)
         
        return geometry

    def get_geometry_from_location(self, location):
        location = location.strip()
        str_format = lfp.get_location_format(location)
        try:
            match str_format:
                case lfp.LocationFormat.STREET_ADDRESS:
                    address = lfp.extract_street_address(location)
                    return self.geocoder.get_street_address_coordinates(address)

                case lfp.LocationFormat.STREET_ADDRESS_RANGE:
                    (address1, address2) =lfp.extract_address_range_street_addresses(location)
                    point1 = self.geocoder.get_street_address_coordinates(address1)
                    point2 = self.geocoder.get_street_address_coordinates(address2)

                    street_segment = LineString([point1, point2])
                    return street_segment

                case lfp.LocationFormat.INTERSECTION:
                    intersect = lfp.extract_intersection(location)
                    intersection = self.geocoder.get_intersection_coordinates(intersect)
                    return intersection

                case lfp.LocationFormat.STREET_SEGMENT_INTERSECTIONS:
                    (intersection1, intersection2) = lfp.extract_segment_intersections(location)
                    point1 = self.geocoder.get_intersection_coordinates(intersection1)
                    point2 = self.geocoder.get_intersection_coordinates(intersection2)

                    street_segment = LineString([point1, point2])
                    return street_segment

                case lfp.LocationFormat.STREET_SEGMENT_ADDRESS_INTERSECTION:
                    (address, intersection) = lfp.extract_segment_address_intersection_info(location)
                    point1 = self.geocoder.get_intersection_coordinates(intersection)
                    point2 = self.geocoder.get_street_address_coordinates(address)

                    street_segment = LineString([point1, point2])
                    return street_segment

                case lfp.LocationFormat.STREET_SEGMENT_INTERSECTION_ADDRESS:
                    (intersection, address) = lfp.extract_segment_intersection_address_info(location)
                    point1 = self.geocoder.get_intersection_coordinates(intersection)
                    point2 = self.geocoder.get_street_address_coordinates(address)
                    # check for returned None for point 1 & point 2

                    street_segment = LineString([point1, point2])
                    return street_segment

                case lfp.LocationFormat.ALLEY:

                    intersections = lfp.extract_alley_intersections(location)

                    points = []
                    for intersection in intersections:
                        points.append(self.geocoder.get_intersection_coordinates(intersection))

                    # remove None values from the array and place points in clockwise order
                    points = [point for point in points if point is not None]

                    points = get_clockwise_sequence(points)

                    coordinates = [(point.x, point.y) for point in points]
                    alley_bounding_box = Polygon(coordinates)
                    return alley_bounding_box

                case _ :
                    print(f"Location text: {location}")
                    print(f"No format match found.\n")
                    return None

        except Exception as e:
            print(f"Location text: {location}")
            print(f"An error occurred: {str(e)}\n")
            return None


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

