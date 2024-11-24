#----------------------------------------------------------------------------------------------------------------------#
# Specific IP:Port - DEFAULT_URL='192.168.86.220:2148' python -m unittest unit-testing/test_anylog_connector.py  -v
#----------------------------------------------------------------------------------------------------------------------#
import os
import unittest
from unittest.mock import patch, MagicMock
from requests.models import Response
from anylog_api.anylog_connector import AnyLogConnector  # Replace with the actual import of your module

DEFAULT_URL = '127.0.0.1:32549'

class TestAnyLogConnector(unittest.TestCase):

    @patch('anylog_api.__support__.check_conn_info')
    @patch('anylog_api.__support__.separate_conn_info')
    @patch('requests.get')
    @patch('requests.put')
    @patch('requests.post')
    def setUp(self, mock_post, mock_put, mock_get, mock_separate_conn_info, mock_check_conn_info):
        # Get the URL from the environment or use the default if not provided
        url_to_use = os.getenv('DEFAULT_URL', DEFAULT_URL)

        print(f"Using URL: {url_to_use}")

        # Mock the check_conn_info and separate_conn_info methods
        mock_check_conn_info.return_value = True
        mock_separate_conn_info.return_value = ('conn_info', ('user', 'password'))  # Mock return values

        # Mock response for requests methods
        self.mock_get_response = MagicMock(spec=Response)
        self.mock_get_response.status_code = 200
        mock_get.return_value = self.mock_get_response

        self.mock_put_response = MagicMock(spec=Response)
        self.mock_put_response.status_code = 200
        mock_put.return_value = self.mock_put_response

        self.mock_post_response = MagicMock(spec=Response)
        self.mock_post_response.status_code = 200
        mock_post.return_value = self.mock_post_response

        # Initialize the connector with mock values
        self.connector = AnyLogConnector(conn=url_to_use, timeout=30)

    @patch('requests.get')
    def test_get_success(self, mock_get):
        headers = {'Authorization': 'Bearer token'}
        mock_get.return_value = self.mock_get_response
        result, error = self.connector.get(headers)

        self.assertEqual(result, self.mock_get_response)
        self.assertIsNone(error)

    @patch('requests.get')
    def test_get_failure(self, mock_get):
        headers = {'Authorization': 'Bearer token'}
        mock_get.return_value = None
        mock_get.side_effect = Exception("Connection failed")

        result, error = self.connector.get(headers)

        self.assertFalse(result)
        self.assertEqual(error, 'Connection failed')

    @patch('requests.put')
    def test_put_success(self, mock_put):
        headers = {'Authorization': 'Bearer token'}
        payload = '{"data": "test"}'
        mock_put.return_value = self.mock_put_response

        result, error = self.connector.put(headers, payload)

        self.assertEqual(result, self.mock_put_response)
        self.assertIsNone(error)

    @patch('requests.put')
    def test_put_failure(self, mock_put):
        headers = {'Authorization': 'Bearer token'}
        payload = '{"data": "test"}'
        mock_put.return_value = None
        mock_put.side_effect = Exception("Put failed")

        result, error = self.connector.put(headers, payload)

        self.assertFalse(result)
        self.assertEqual(error, 'Put failed')

    @patch('requests.post')
    def test_post_success(self, mock_post):
        headers = {'Authorization': 'Bearer token'}
        payload = '{"data": "test"}'
        mock_post.return_value = self.mock_post_response

        result, error = self.connector.post(headers, payload)

        self.assertEqual(result, self.mock_post_response)
        self.assertIsNone(error)

    @patch('requests.post')
    def test_post_failure(self, mock_post):
        headers = {'Authorization': 'Bearer token'}
        payload = '{"data": "test"}'
        mock_post.return_value = None
        mock_post.side_effect = Exception("Post failed")

        result, error = self.connector.post(headers, payload)

        self.assertFalse(result)
        self.assertEqual(error, 'Post failed')

    @patch('requests.get')
    def test_get_error_status_code(self, mock_get):
        headers = {'Authorization': 'Bearer token'}
        mock_get.return_value = self.mock_get_response
        self.mock_get_response.status_code = 500  # Simulate error status code

        result, error = self.connector.get(headers)

        self.assertFalse(result)
        self.assertEqual(error, 500)

    @patch('requests.put')
    def test_put_error_status_code(self, mock_put):
        headers = {'Authorization': 'Bearer token'}
        payload = '{"data": "test"}'
        mock_put.return_value = self.mock_put_response
        self.mock_put_response.status_code = 500  # Simulate error status code

        result, error = self.connector.put(headers, payload)

        self.assertFalse(result)
        self.assertEqual(error, '500')

    @patch('requests.post')
    def test_post_error_status_code(self, mock_post):
        headers = {'Authorization': 'Bearer token'}
        payload = '{"data": "test"}'
        mock_post.return_value = self.mock_post_response
        self.mock_post_response.status_code = 500  # Simulate error status code

        result, error = self.connector.post(headers, payload)

        self.assertFalse(result)
        self.assertEqual(error, '500')


if __name__ == '__main__':
    unittest.main()
