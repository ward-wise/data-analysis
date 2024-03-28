from src.chicago_participatory_urbanism.geocoder_local import Geocoder
import pytest
from unittest.mock import patch


@patch('src.chicago_participatory_urbanism.geocoder_local.gpd.read_file')
@patch('src.chicago_participatory_urbanism.geocoder_local.pd.read_csv')
def test_geocoder_local_initializes_correctly_with_fake_files(mock_read_csv, mock_read_file):
    test_geocoder = Geocoder()
    assert test_geocoder.address_points_df == mock_read_csv.return_value
    assert test_geocoder.street_center_lines_gdf == mock_read_file.return_value


@pytest.mark.integration_test
def test_geocoder_local_initializes_correctly_with_real_files():
    test_geocoder = Geocoder()
    assert len(test_geocoder.address_points_df) == 582504
    assert len(test_geocoder.street_center_lines_gdf) == 56338
