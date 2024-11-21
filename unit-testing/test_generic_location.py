import unittest
from unittest.mock import MagicMock, patch
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.geolocation import get_location  # Assuming get_location is in 'generic.geolocation'

# Mocked GEO_URL for testing
GEO_URL = "https://ipinfo.io/json"


class TestGetLocation(unittest.TestCase):

    def setUp(self):
        # Create a mock for AnyLogConnector
        self.mock_conn = MagicMock(spec=anylog_connector.AnyLogConnector)
        # Sample parameters to use in tests
        self.params = {
            'location': 'New York',
            'country': 'USA',
            'state': 'NY',
            'city': 'New York',
            'loc_info': {'loc': '40.7128,-74.0060', 'city': 'New York'}
        }

    @patch('anylog_api.generic.geolocation.execute_publish_cmd')
    @patch('anylog_api.generic.geolocation.get_dictionary')
    @patch('anylog_api.generic.geolocation.get_help')
    @patch('anylog_api.__support__.json_loads')
    def test_get_location_success_from_params(self, mock_json_loads, mock_get_help, mock_get_dictionary,
                                              mock_execute_publish_cmd):
        # Test case where 'loc_info' is already present in the params
        location = get_location(self.mock_conn, self.params, exception=False)
        self.assertEqual(location, self.params['loc_info'])  # Should return loc_info from params

    @patch('anylog_api.generic.geolocation.execute_publish_cmd')
    @patch('anylog_api.generic.geolocation.get_dictionary')
    @patch('anylog_api.generic.geolocation.get_help')
    @patch('anylog_api.__support__.json_loads')
    def test_get_location_success_from_configuration(self, mock_json_loads, mock_get_help, mock_get_dictionary,
                                                     mock_execute_publish_cmd):
        # Simulate missing loc_info, but location-related params exist
        params_without_loc_info = {
            'location': 'New York',
            'country': 'USA',
            'state': 'NY',
            'city': 'New York'
        }

        location = get_location(self.mock_conn, params_without_loc_info, exception=False)

        # Assert that the location dictionary contains the expected keys
        self.assertEqual(location, {'loc': 'New York', 'country': 'USA', 'state': 'NY', 'city': 'New York'})

    @patch('anylog_api.generic.geolocation.execute_publish_cmd')
    @patch('anylog_api.generic.geolocation.get_dictionary')
    @patch('anylog_api.generic.geolocation.get_help')
    @patch('anylog_api.__support__.json_loads')
    def test_get_location_success_from_execute_publish_cmd(self, mock_json_loads, mock_get_help, mock_get_dictionary,
                                                           mock_execute_publish_cmd):
        # Test case where location is missing and an API call is made
        self.params = {}  # Empty params to force execute_publish_cmd to be called
        mock_execute_publish_cmd.return_value = True
        mock_get_dictionary.return_value = {'loc_info': {'loc': '40.7128,-74.0060', 'city': 'New York'}}

        location = get_location(self.mock_conn, self.params, exception=False)

        # Assert that location was fetched from execute_publish_cmd
        self.assertEqual(location, {'loc': '40.7128,-74.0060', 'city': 'New York'})

    @patch('anylog_api.generic.geolocation.execute_publish_cmd')
    @patch('anylog_api.generic.geolocation.get_dictionary')
    @patch('anylog_api.generic.geolocation.get_help')
    @patch('anylog_api.__support__.json_loads')
    def test_get_location_invalid_location_format(self, mock_json_loads, mock_get_help, mock_get_dictionary,
                                                  mock_execute_publish_cmd):
        # Test case where location is returned as a string but is invalid JSON
        self.params = {'loc_info': "{'loc': 'invalid_format'}"}  # Malformed JSON string
        mock_json_loads.return_value = None  # Simulate json_loads failing

        location = get_location(self.mock_conn, self.params, exception=False)

        # Assert location is empty or the expected fallback behavior
        self.assertEqual(location, {'loc': 'invalid_format'})

    # @patch('anylog_api.generic.geolocation.execute_publish_cmd')
    # @patch('anylog_api.generic.geolocation.get_help')
    # def test_get_location_view_help(self, mock_get_help, mock_execute_publish_cmd):
    #     # Test case for when view_help=True
    #     self.params = {}
    #     mock_execute_publish_cmd.return_value = True  # Simulate successful cmd execution
    #
    #     location = get_location(self.mock_conn, self.params, view_help=True, exception=False)
    #
    #     # Check if the get_help function was called with the correct parameters
    #     mock_get_help.assert_called_with(conn=self.mock_conn,
    #                                      cmd='loc_info = rest get where url = https://ipinfo.io/json', exception=False)

    @patch('anylog_api.generic.geolocation.execute_publish_cmd')
    @patch('anylog_api.generic.geolocation.get_help')
    def test_get_location_return_cmd(self, mock_get_help, mock_execute_publish_cmd):
        # Test case for when return_cmd=True
        self.params = {}
        location = get_location(self.mock_conn, self.params, return_cmd=True, exception=False)

        # Assert that the returned command is as expected
        self.assertEqual(location, 'loc_info = rest get where url = https://ipinfo.io/json')

    @patch('anylog_api.generic.geolocation.execute_publish_cmd')
    @patch('anylog_api.generic.geolocation.get_help')
    def test_get_location_exception_handling(self, mock_get_help, mock_execute_publish_cmd):
        # Test exception handling when an error occurs in the function
        self.params = {}
        mock_execute_publish_cmd.side_effect = Exception("Test exception")

        with self.assertRaises(Exception):
            get_location(self.mock_conn, self.params, exception=True)


if __name__ == '__main__':
    unittest.main()
