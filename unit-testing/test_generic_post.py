import unittest
from unittest.mock import Mock, patch

from idna import valid_label_length

from anylog_api.anylog_connector import AnyLogConnector
from anylog_api.generic.post import set_params, set_node_name, set_path


class TestAnyLogGenericPOST(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock the connection to AnyLog node
        cls.connector = Mock(AnyLogConnector)


    @patch('anylog_api.generic.post.execute_publish_cmd')
    @patch('anylog_api.generic.post.get_help')
    def test_set_params_with_view_help(self, mock_get_help, mock_execute_publish_cmd):
        # Test data with view_help = True
        params = {
            "key1": "value1"
        }

        # Mock the behavior of execute_publish_cmd and get_help
        mock_execute_publish_cmd.return_value = None  # Simulate success
        mock_get_help.return_value = None  # Simulate no help response

        # Call the method with view_help=True
        set_params(self.connector, params, view_help=True)

        # Assert that get_help was called with the expected command
        for param in params:
            mock_get_help.assert_called_with(
                conn=self.connector,
                cmd=f"{param} = {params[param]}",
                exception=False
            )

        # Ensure execute_publish_cmd was not called
        mock_execute_publish_cmd.assert_not_called()


    @patch('anylog_api.generic.post.execute_publish_cmd')
    def test_set_node_name(self, mock_execute_publish_cmd):
        # Test data
        node_name = "test-node"
        headers = {
            "command": f"set node name {node_name}",
            "User-Agent": "AnyLog/1.23"
        }

        # Mock the behavior of execute_publish_cmd
        mock_execute_publish_cmd.return_value = True  # Simulate success

        # Call the method
        result = set_node_name(self.connector, node_name)

        # Check if the expected command was passed to execute_publish_cmd
        mock_execute_publish_cmd.assert_called_with(
            conn=self.connector,
            cmd='post',
            headers=headers,
            payload=None,
            exception=False
        )

        # Assert the result is the same as the command
        self.assertTrue(result)


    @patch('anylog_api.generic.post.execute_publish_cmd')
    def test_set_node_name(self, mock_execute_publish_cmd):
        # Test data
        node_name = "test-node"
        headers = {
            "command": f"set node name {node_name}",
            "User-Agent": "AnyLog/1.23"
        }

        # Mock the behavior of execute_publish_cmd
        mock_execute_publish_cmd.return_value = True  # Simulate success

        # Call the method
        result = set_node_name(self.connector, node_name)

        # Check if the expected command was passed to execute_publish_cmd
        mock_execute_publish_cmd.assert_called_with(
            conn=self.connector,
            cmd='post',
            headers=headers,
            payload=None,
            exception=False
        )

        # Assert the result is the same as the command
        self.assertTrue(result)

    @patch('anylog_api.generic.post.execute_publish_cmd')
    def test_set_path(self, mock_execute_publish_cmd):
        # Test data
        valid_paths = [
            "C:/Users/username/Documents",  # Windows path
            "/app/AnyLog-Network/",        # Linux path
            "/home/username/documents"     # Linux path
        ]

        # Mock the behavior of execute_publish_cmd
        mock_execute_publish_cmd.return_value = True  # Simulate success

        # Iterate through the valid paths and test
        for path in valid_paths:
            result = set_path(conn=self.connector, path=path, destination=None, return_cmd=False, view_help=False,
                              exception=False)  # Correct function call here
            self.assertTrue(result)  # Assert that the result is a success (True) or as expected

        result = set_path(conn=self.connector, path="/app/AnyLog-Network/", destination=None, return_cmd=True, view_help=False,
                              exception=False)
        assert result == "set anylog home /app/AnyLog-Network/"


if __name__ == '__main__':
    unittest.main()
