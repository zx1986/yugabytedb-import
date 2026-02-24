import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import main


class TestMainCLI(unittest.TestCase):
    @patch("main.run_baseline")
    @patch("main.init_db_schema")
    @patch("main.generate_test_data")
    def test_single_mode(self, mock_gen, mock_init, mock_baseline):
        mock_baseline.return_value = (100, 1.0, 100.0)
        with patch("sys.argv", ["main.py", "--mode", "single", "--file", "test.csv"]):
            main()
        mock_init.assert_called_once()
        mock_baseline.assert_called_once_with("test.csv")

    @patch("main.run_parallel")
    @patch("main.init_db_schema")
    def test_parallel_mode(self, mock_init, mock_parallel):
        mock_parallel.return_value = (100, 0.5, 200.0)
        with patch("sys.argv", [
            "main.py", "--mode", "parallel", "--file", "test.csv",
            "--workers", "4", "--chunk-size", "50",
        ]):
            main()
        mock_parallel.assert_called_once_with("test.csv", 4, 50)

    @patch("main.run_baseline")
    @patch("main.clear_test_data")
    def test_no_init_flag(self, mock_clear, mock_baseline):
        mock_baseline.return_value = (10, 0.1, 100.0)
        with patch("sys.argv", [
            "main.py", "--mode", "single", "--file", "t.csv", "--no-init",
        ]):
            main()
        mock_clear.assert_called_once()


if __name__ == "__main__":
    unittest.main()
