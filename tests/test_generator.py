import os
import sys
import tempfile
import unittest

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from test_data_generator import generate_test_data, _random_name


class TestRandomName(unittest.TestCase):
    def test_default_length(self):
        name = _random_name()
        self.assertEqual(len(name), 15)
        self.assertTrue(name.isalpha())

    def test_custom_length(self):
        name = _random_name(5)
        self.assertEqual(len(name), 5)


class TestGenerateTestData(unittest.TestCase):
    def test_generates_correct_row_count(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name
        # Ensure file doesn't exist before generation
        os.unlink(tmp_path)
        try:
            generate_test_data(tmp_path, num_rows=100)
            with open(tmp_path, "r") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 100)
        finally:
            os.unlink(tmp_path)

    def test_csv_columns(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name
        os.unlink(tmp_path)
        try:
            generate_test_data(tmp_path, num_rows=5)
            with open(tmp_path, "r") as f:
                for line in f:
                    # id, name, email, score, created_at
                    parts = line.strip().split(",")
                    self.assertEqual(len(parts), 5, f"Expected 5 columns, got: {parts}")
                    self.assertTrue(parts[0].isdigit())
                    self.assertIn("@example.com", parts[2])
        finally:
            os.unlink(tmp_path)

    def test_skips_existing_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp.write("existing\n")
            tmp_path = tmp.name
        try:
            generate_test_data(tmp_path, num_rows=10)
            with open(tmp_path, "r") as f:
                content = f.read()
            self.assertEqual(content, "existing\n")
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
