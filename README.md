# Chicago Participatory Urbanism

Every year, Chicago alders get $1.5 million to spend at their discretion on capital improvements on their ward through the city's Aldermanic Menu Program. Their spending is publicly available in PDF format in the [Chicago Capital Improvement Archive](https://www.chicago.gov/city/en/depts/obm/provdrs/cap_improve/svcs/cip-archive.html). We are in the process of extracting and geocoding this data. 

Check out the GitHub issues for things to work on.

# Getting Started/Installing the Repo
1. Clone the repo.
2. Run the following command in the terminal:
```
pip install .
```

# Work Flow
* Extract data from PDFs
* Post-process data (name cleanup, field seperation, categorization)
* Geocode location data
    * Identify location format
    * Parse location into collection of street numbers or street intersections
    * Get GPS coordinates from street numbers and street interesections
    * Combine coordinates into point(s), lines, or polygons
* Post-process geo-data 
    * Interpolate lines and polygons into point clouds for heatmapping

# Code Overview
## Scripts
* ward_spending_pdf_data_extraction - converts CIP aldermanic menu spending PDFs into CSVs
* ward_spending_post_processing - post-processes PDF data, making fixes to columns and categorizing items
* ward_spending_geocoding - gecodes the CSV data, outputtinga geoJSON
### Upcoming Bike Lanes
* bike_geocoding_script - one-off, uses the ward wise libraries to geocode CDOT upcoming bike lane data

## Chicago Participatory Urbanism libraries
* ward_spending.address_geocoding - use to convert location text into geo-coded geometry data
    * ward_spending.address_format_processing - use to parse location text into street numbers and street intersections
    * geocoder - use to geocode street numbers and street intersections



# Ideas
[Brainstorming Doc](https://docs.google.com/document/d/1vKIF3epFqXw7eDmwkk1lHWOB95OQjqQNfs-ehjCkP7E/edit?usp=sharing)
