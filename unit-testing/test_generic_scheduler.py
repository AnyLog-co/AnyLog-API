import requests
import unittest
from unittest.mock import MagicMock
import anylog_api.anylog_connector as anylog_connector
from anylog_api.generic.scheduler import (
    run_scheduler,
    run_schedule_task,
    get_scheduler
)

def mock_response(json_data=None, text_data=None):
    """
    Helper function to create a mock response.
    :param json_data: Data to be returned by json() method.
    :param text_data: Data to be returned as the raw response text.
    :return: A MagicMock object simulating a requests.Response.
    """
    response = MagicMock(spec=requests.Response)
    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.side_effect = AttributeError("No JSON data available")
    if text_data is not None:
        response.text = text_data
    return response

class TestAnylogConnectorSupport(unittest.TestCase):
    def setUp(self):
        # Mock connection object
        self.mock_conn = MagicMock(spec=anylog_connector.AnyLogConnector)

    def test_run_scheduler_success(self):
        # Simulate success of POST request
        self.mock_conn.post.return_value = (True, None)

        # Run the scheduler with valid arguments
        status = run_scheduler(self.mock_conn, schedule_id=1, exception=False)
        self.assertTrue(status)

    def test_run_scheduler_invalid_schedule_id_no_exception(self):
        # Test invalid schedule_id (non-positive integer) without raising an exception
        status = run_scheduler(self.mock_conn, schedule_id=-1, exception=False)
        self.assertIsNone(status)

    def test_run_scheduler_exception_on_invalid_schedule_id(self):
        # Test invalid schedule_id (non-positive integer) with exception
        with self.assertRaises(ValueError):
            run_scheduler(self.mock_conn, schedule_id=-1, exception=True)

    def test_run_scheduler_invalid_schedule_id_no_id_provided(self):
        # Test missing schedule_id (None) without exception
        status = run_scheduler(self.mock_conn, schedule_id=None, exception=False)
        self.assertEqual(status, None)

    def test_run_scheduler_exception_on_missing_schedule_id(self):
        # Test missing schedule_id (None) with exception
        with self.assertRaises(KeyError):
            run_scheduler(self.mock_conn, schedule_id=None, exception=True)

    def test_run_scheduler_return_cmd(self):
        # Test returning the command string without executing
        command = run_scheduler(self.mock_conn, schedule_id=1, return_cmd=True)
        self.assertEqual(command, 'run scheduler 1')

    def test_run_scheduler_invalid_schedule_id(self):
        # Test invalid schedule_id (non-positive integer) with exception=True
        with self.assertRaises(ValueError):
            run_scheduler(self.mock_conn, schedule_id=0, exception=True)

    def test_run_scheduler_return_cmd_with_invalid_schedule_id(self):
        # Test that the command is returned without execution if schedule_id is invalid
        command = run_scheduler(self.mock_conn, schedule_id=0, return_cmd=True)
        self.assertIsNone(command, 'run scheduler 0')

    def test_get_scheduler_success(self):
        # Simulate success of GET request
        self.mock_conn.get.return_value = (MagicMock(), None)
        self.mock_conn.get.return_value[0].json.return_value = {"success": True}

        # Test retrieving scheduler with valid schedule_id
        status = get_scheduler(self.mock_conn, schedule_id=1, exception=False)
        self.assertEqual(status, {"success": True})

    def test_get_scheduler_invalid_schedule_id(self):
        # Test invalid schedule_id (non-integer)
        with self.assertRaises(ValueError):
            get_scheduler(self.mock_conn, schedule_id="invalid", exception=True)

    def test_get_scheduler_invalid_schedule_id_no_exception(self):
        # Simulate a mocked response for conn.get
        mocked_response = mock_response(json_data={"message": "Invalid ID ignored"})
        self.mock_conn.get.return_value = (mocked_response, None)

        # Call the function with an invalid schedule ID and exception=False
        status = get_scheduler(self.mock_conn, schedule_id="invalid", exception=False)

        # Assert the function returns None due to invalid ID handling
        self.assertEqual(status, {'message': 'Invalid ID ignored'})

    def test_get_scheduler_return_cmd(self):
        # Test returning the generated command
        command = get_scheduler(self.mock_conn, schedule_id=1, return_cmd=True)
        self.assertEqual(command, 'get scheduler 1')

    def test_run_schedule_task_success(self):
        # Simulate success of POST request
        self.mock_conn.post.return_value = (True, None)

        # Test scheduling a task with valid time_interval
        status = run_schedule_task(self.mock_conn, name="Test Task", time_interval="minute", task="run_task", exception=False)
        self.assertTrue(status)

    def test_run_schedule_task_invalid_interval(self):
        # Test invalid time_interval
        with self.assertRaises(ValueError):
            run_schedule_task(self.mock_conn, name="Test Task", time_interval="invalid", task="run_task", exception=True)

    def test_run_schedule_task_return_cmd(self):
        # Test returning the generated command
        command = run_schedule_task(self.mock_conn, name="Test Task", time_interval="minute", task="run_task", return_cmd=True)
        self.assertEqual(command, 'schedule name=Test Task and time=minute and task run_task')

if __name__ == "__main__":
    unittest.main()
