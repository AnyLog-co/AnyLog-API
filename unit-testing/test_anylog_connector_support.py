#----------------------------------------------------------------------------------------------------------------------#
# List tests: python -m unittest unit-test/test_anylog_connector_support.py -v
# Specific test: python -m unittest unit-test/test_anylog_connector_support.py -v -k test_extract_get_results_success
#----------------------------------------------------------------------------------------------------------------------#
import unittest
from unittest.mock import MagicMock
import requests
import anylog_api.anylog_connector as anylog_connector
from anylog_api.anylog_connector_support import (
    extract_get_results,
    execute_publish_cmd
)


class TestAnylogConnectorSupport(unittest.TestCase):
    def setUp(self):
        # Mock connection object
        self.mock_conn = MagicMock(spec=anylog_connector.AnyLogConnector)

    def test_extract_get_results_success(self):
        headers = {"command": "test_cmd"}
        self.mock_conn.get.return_value = (MagicMock(), None)
        self.mock_conn.get.return_value[0].json.return_value = {"success": True}
        result = extract_get_results(self.mock_conn, headers, exception=False)
        self.assertEqual(result, {"success": True})

    def test_extract_get_results_failure(self):
        headers = {"command": "test_cmd"}
        self.mock_conn.get.return_value = (False, "404")
        with self.assertRaises(requests.RequestException):
            extract_get_results(self.mock_conn, headers, exception=True)

    def test_execute_publish_cmd_post_success(self):
        headers = {"command": "test_cmd"}
        self.mock_conn.post.return_value = (True, None)
        status = execute_publish_cmd(self.mock_conn, "POST", headers, payload="data", exception=False)
        self.assertTrue(status)

    def test_execute_publish_cmd_put_success(self):
        headers = {"command": "test_cmd"}
        self.mock_conn.put.return_value = (True, None)
        status = execute_publish_cmd(self.mock_conn, "PUT", headers, payload="data", exception=False)
        self.assertTrue(status)

    def test_execute_publish_cmd_failure_with_exception(self):
        headers = {"command": "test_cmd"}
        self.mock_conn.post.return_value = (False, "500")
        with self.assertRaises(requests.RequestException):
            execute_publish_cmd(self.mock_conn, "POST", headers, payload="data", exception=True)

    def test_execute_publish_cmd_invalid_command(self):
        headers = {"command": "test_cmd"}
        status = execute_publish_cmd(self.mock_conn, "INVALID", headers, payload="data", exception=False)
        self.assertTrue(status)  # No exception raised, invalid command is treated as noop


if __name__ == "__main__":
    unittest.main()
