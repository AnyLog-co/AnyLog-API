import unittest
from unittest.mock import Mock, patch
from anylog_api.anylog_connector import AnyLogConnector
from anylog_api.generic.get import (
    get_help, get_status, get_license_key, get_dictionary, get_node_name,
    get_hostname, get_version, get_processes, get_event_log, get_error_log, get_echo_log
)


class TestAnyLogGenericGET(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_connector = Mock(spec=AnyLogConnector)

    # @patch('anylog_api.generic.get.extract_get_results')
    # def test_get_help(self, mock_extract):
    #     mock_extract.return_value = "Help information"
    #     result = get_help(self.mock_connector, cmd="get status")
    #     self.assertIsNone(result)  # Since `get_help` just prints
    #     mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_status(self, mock_extract):
        mock_extract.return_value = {"Status": "running"}
        status = get_status(self.mock_connector)
        self.assertTrue(status)
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_license_key(self, mock_extract):
        mock_extract.return_value = "ABC123-LICENSE-KEY"
        license_key = get_license_key(self.mock_connector)
        self.assertEqual(license_key, "ABC123-LICENSE-KEY")
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_dictionary(self, mock_extract):
        mock_extract.return_value = {"key1": "value1", "key2": "value2"}
        dictionary = get_dictionary(self.mock_connector)
        self.assertEqual(dictionary, {"key1": "value1", "key2": "value2"})
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_node_name(self, mock_extract):
        mock_extract.return_value = "TestNode"
        node_name = get_node_name(self.mock_connector)
        self.assertEqual(node_name, "TestNode")
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_hostname(self, mock_extract):
        mock_extract.return_value = "test-host"
        hostname = get_hostname(self.mock_connector)
        self.assertEqual(hostname, "test-host")
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_version(self, mock_extract):
        mock_extract.return_value = "v1.2.3"
        version = get_version(self.mock_connector)
        self.assertEqual(version, "v1.2.3")
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_processes(self, mock_extract):
        mock_extract.return_value = {
            "TCP": {"Status": "Running"},
            "REST": {"Status": "Not declared"}
        }
        processes = get_processes(self.mock_connector)
        self.assertIn("TCP", processes)
        self.assertEqual(processes["TCP"]["Status"], "Running")
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_event_log(self, mock_extract):
        mock_extract.return_value = [{"timestamp": "2024-11-25T12:00:00Z", "event": "Test Event"}]
        event_log = get_event_log(self.mock_connector)
        self.assertIsInstance(event_log, list)
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_error_log(self, mock_extract):
        mock_extract.return_value = [{"timestamp": "2024-11-25T12:00:00Z", "error": "Test Error"}]
        error_log = get_error_log(self.mock_connector)
        self.assertIsInstance(error_log, list)
        mock_extract.assert_called_once()

    @patch('anylog_api.generic.get.extract_get_results')
    def test_get_echo_log(self, mock_extract):
        mock_extract.return_value = [{"timestamp": "2024-11-25T12:00:00Z", "echo": "Test Echo"}]
        echo_log = get_echo_log(self.mock_connector)
        self.assertIsInstance(echo_log, list)
        mock_extract.assert_called_once()


if __name__ == "__main__":
    unittest.main()
