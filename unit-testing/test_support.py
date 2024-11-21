import unittest
import json
from anylog_api.__support__ import (
    json_loads,
    json_dumps,
    check_conn_info,
    separate_conn_info,
    check_interval
)


class TestSupportFunctions(unittest.TestCase):

    def test_json_loads_success(self):
        content = '{"key": "value"}'
        result = json_loads(content)
        self.assertEqual(result, {"key": "value"})

    def test_json_loads_failure(self):
        content = '{"key": value}'  # Invalid JSON
        with self.assertRaises(json.JSONDecodeError):
            json_loads(content, exception=True)

    def test_json_loads_no_exception(self):
        content = '{"key": value}'  # Invalid JSON
        result = json_loads(content, exception=False)
        self.assertIsNone(result)

    def test_json_dumps_success(self):
        content = {"key": "value"}
        result = json_dumps(content)
        self.assertEqual(result, '{"key": "value"}')

    def test_json_dumps_with_indent(self):
        content = {"key": "value"}
        result = json_dumps(content, indent=2)
        self.assertEqual(result, '{\n  "key": "value"\n}')

    def test_json_dumps_failure(self):
        content = {"key": set([1, 2, 3])}  # JSON cannot serialize sets
        with self.assertRaises(json.JSONDecodeError):
            json_dumps(content, exception=True)

    def test_json_dumps_no_exception(self):
        content = {"key": set([1, 2, 3])}  # JSON cannot serialize sets
        result = json_dumps(content, exception=False)
        self.assertIsNone(result)

    def test_check_conn_info_valid(self):
        conn = "127.0.0.1:32048"
        result = check_conn_info(conn)
        self.assertTrue(result)

    def test_check_conn_info_invalid_format(self):
        conn = "invalid_conn"
        with self.assertRaises(ValueError):
            check_conn_info(conn)

    def test_separate_conn_info_valid(self):
        conn = "user:password@127.0.0.1:32048"
        conn_info, auth = separate_conn_info(conn)
        self.assertEqual(conn_info, "127.0.0.1:32048")
        self.assertEqual(auth, ("user", "password"))

    def test_separate_conn_info_invalid_format(self):
        conn = "127.0.0.1:32048"
        conn_info, auth = separate_conn_info(conn)
        self.assertEqual(conn_info, "127.0.0.1:32048")
        self.assertEqual(auth, ())

    def test_check_interval_valid(self):
        time_interval = "10 minutes"
        result = check_interval(time_interval)
        self.assertTrue(result)

    def test_check_interval_invalid_format(self):
        time_interval = "10 min"
        result = check_interval(time_interval, exception=False)
        self.assertFalse(result)

    def test_check_interval_invalid_with_exception(self):
        time_interval = "10 min"
        with self.assertRaises(ValueError):
            check_interval(time_interval, exception=True)


if __name__ == "__main__":
    unittest.main()
