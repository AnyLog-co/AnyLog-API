import unittest
from unittest.mock import patch, MagicMock
from anylog_api.anylog_connector import AnyLogConnector
from anylog_api.__support__ import check_ip, check_conn_info


class TestAnyLogConnector(unittest.TestCase):
    def test_valid_conn(self):
        # Valid connections should pass
        valid_connections = ['10.10.1.15:32149', 'localhost:32048']
        for conn in valid_connections:
            self.assertTrue(check_ip(conn), f"Valid connection failed: {conn}")

            # Invalid connections should fail
            invalid_connections = [
                "10.10.1.256:32149",  # Invalid IP (octet > 255),
                "10.10.1.15:70000",    # Invalid port (exceeds 65535)
                "localhost:0",         # Invalid port (less than 1)
                "10.10.1.15:",         # Missing port
                ":32149",              # Missing IP/host
                "localhost:abcd",      # Non-numeric port
                "localhost-32048",     # Incorrect separator (`-` instead of `:`)
                "10.10.1.15 32149",    # Missing colon (`:`) between host and port
                "localhost:32048extra",# Extra characters after the port
                "10.10.1.15::32149",   # Extra colon
                "localhost",           # Missing port
                "10.10.1.15",          # Missing port
                "localhost: 32149",    # Space after the colon
            ]

            for conn in invalid_connections:
                with self.subTest(conn=conn):  # SubTest allows reporting which case fails
                    with self.assertRaises(ValueError):
                        check_ip(conn)


    @patch('anylog_api.__support__.check_conn_info')
    @patch('anylog_api.__support__.separate_conn_info')
    def test_initialization_valid_conn(self, mock_separate_conn_info, mock_check_conn_info):
        # Arrange
        mock_check_conn_info.return_value = True
        mock_separate_conn_info.return_value = ('10.10.1.15:32149', ('user', 'pass'))
        conn = '10.10.1.15:32149:user:pass'

        # Act
        connector = AnyLogConnector(conn=conn, timeout=30)

        # Assert
        self.assertEqual(connector.conn, '10.10.1.15:32149')
        self.assertEqual(connector.auth, ('user', 'pass'))
        self.assertEqual(connector.timeout, 30)

    def test_initialization_invalid_conn_format(self):
        # Arrange
        conn = 'invalid_conn_format'

        # Act / Assert
        with self.assertRaises(ValueError) as context:
            AnyLogConnector(conn=conn, timeout=30)

        self.assertIn("Invalid connection format", str(context.exception))

    def test_initialization_invalid_timeout(self):
        # Arrange
        conn = '10.10.1.15:32149'

        # Act / Assert
        with self.assertRaises(ValueError) as context:
            AnyLogConnector(conn=conn, timeout="invalid_timeout")

        self.assertIn("Timeout value must be of type int", str(context.exception))

    @patch('requests.get')
    def test_get_successful(self, mock_get):
        # Arrange
        conn = '10.10.1.15:32149'
        connector = AnyLogConnector(conn=conn, timeout=30)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        headers = {"command": "get status"}

        # Act
        response, error = connector.get(headers=headers)

        # Assert
        self.assertTrue(response)
        self.assertIsNone(error)
        mock_get.assert_called_once_with(
            f'http://{connector.conn}', headers=headers, auth=connector.auth, timeout=connector.timeout
        )

    @patch('requests.get')
    def test_get_unsuccessful_status_code(self, mock_get):
        # Arrange
        conn = '10.10.1.15:32149'
        connector = AnyLogConnector(conn=conn, timeout=30)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        headers = {"command": "get status"}

        # Act
        response, error = connector.get(headers=headers)

        # Assert
        self.assertFalse(response)
        self.assertEqual(error, 404)

    @patch('requests.get')
    def test_get_exception(self, mock_get):
        # Arrange
        conn = '10.10.1.15:32149'
        connector = AnyLogConnector(conn=conn, timeout=30)
        mock_get.side_effect = Exception("Connection error")
        headers = {"command": "get status"}

        # Act
        response, error = connector.get(headers=headers)

        # Assert
        self.assertFalse(response)
        self.assertEqual(error, "Connection error")

    @patch('requests.put')
    def test_put_successful(self, mock_put):
        # Arrange
        conn = '10.10.1.15:32149'
        connector = AnyLogConnector(conn=conn, timeout=30)
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_put.return_value = mock_response
        headers = {"command": "put data"}
        payload = "payload data"

        # Act
        response, error = connector.put(headers=headers, payload=payload)

        # Assert
        self.assertTrue(response)
        self.assertIsNone(error)

    @patch('requests.post')
    def test_post_unsuccessful_status_code(self, mock_post):
        # Arrange
        conn = '10.10.1.15:32149'
        connector = AnyLogConnector(conn=conn, timeout=30)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        headers = {"command": "post data"}
        payload = "payload data"

        # Act
        response, error = connector.post(headers=headers, payload=payload)

        # Assert
        self.assertFalse(response)
        self.assertEqual(error, "500")

    @patch('requests.post')
    def test_post_exception(self, mock_post):
        # Arrange
        conn = '10.10.1.15:32149'
        connector = AnyLogConnector(conn=conn, timeout=30)
        mock_post.side_effect = Exception("Connection error")
        headers = {"command": "post data"}
        payload = "payload data"

        # Act
        response, error = connector.post(headers=headers, payload=payload)

        # Assert
        self.assertFalse(response)
        self.assertEqual(error, "Connection error")


if __name__ == '__main__':
    unittest.main()
