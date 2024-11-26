import unittest
from unittest.mock import Mock, patch
from anylog_api.anylog_connector import AnyLogConnector
from anylog_api.anylog_connector_support import  extract_get_results, execute_publish_cmd


class TestAnyLogConnectorSupport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connector = AnyLogConnector(conn='10.10.1.3:32849', timeout=30)

    @patch("anylog_api.anylog_connector.AnyLogConnector.get")
    def test_extract_get_results_success(self, mock_get):
        # Mocking the return value of AnyLogConnector.get
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = (mock_response, None)

        headers = {"command": "test_command"}
        result = extract_get_results(conn=self.connector, headers=headers)
        self.assertEqual(result, {"key": "value"})
        mock_get.assert_called_once_with(headers=headers)

    @patch("anylog_api.anylog_connector.AnyLogConnector.get")
    def test_extract_get_results_failure(self, mock_get):
        # Simulating a failure
        mock_get.return_value = (False, "500")
        headers = {"command": "test_command"}

        with self.assertRaises(Exception):  # Change as per specific exceptions
            extract_get_results(conn=self.connector, headers=headers, exception=True)

    @patch("anylog_api.anylog_connector.AnyLogConnector.post")
    def test_execute_publish_cmd_post_success(self, mock_post):
        # Mocking successful POST request
        mock_post.return_value = (True, None)

        headers = {"command": "test_post"}
        result = execute_publish_cmd(conn=self.connector, cmd="POST", headers=headers, payload="data")
        self.assertTrue(result)
        mock_post.assert_called_once_with(headers=headers, payload="data")

    @patch("anylog_api.anylog_connector.AnyLogConnector.put")
    def test_execute_publish_cmd_put_failure(self, mock_put):
        # Mocking a failed PUT request
        mock_put.return_value = (False, "500")

        headers = {"command": "test_put"}
        result = execute_publish_cmd(conn=self.connector, cmd="PUT", headers=headers, payload="data")
        self.assertFalse(result)
        mock_put.assert_called_once_with(headers=headers, payload="data")




if __name__ == "__main__":
    unittest.main()
