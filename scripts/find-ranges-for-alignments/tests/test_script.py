import unittest
import subprocess
import json

class TestFindRangesForAlignments(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_output(self):
        # Run the script with the sample file as input
        result = subprocess.run(['python', 'scripts/find-ranges-for-alignments/find-ranges-for-alignments.py', 'scripts/find-ranges-for-alignments/tests/sample_ingestion_file.jsonl',], capture_output=True, text=True)
        # print(result.stdout)
        
        with open('scripts/find-ranges-for-alignments/tests/sample_ingestion_file_final_output.jsonl', 'r') as f:
            output = f.read()

        # Check if the script executed successfully
        # self.assertEqual(result.returncode, 0, f"Script failed with error: {result.stderr}")

        # Load the expected output from a file (you'll need to create this file)
        with open('scripts/find-ranges-for-alignments/tests/expected_output.jsonl', 'r') as f:
            expected_output = f.read()

        # Convert both the actual and expected outputs to dictionaries
        actual_output_dict = json.loads(output)
        expected_output_dict = json.loads(expected_output)

        # Check that the script's output matches the expected output
        self.assertEqual(expected_output_dict, actual_output_dict)

if __name__ == '__main__':
    unittest.main()
