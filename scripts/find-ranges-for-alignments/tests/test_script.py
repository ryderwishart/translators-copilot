import unittest
import os, json
import subprocess

class TestScriptOutput(unittest.TestCase):

    def setUp(self):
        # This is run before each test
        self.output_filename = 'expected_output_final_output.jsonl'
        self.maxDiff = None


    def test_output_file_exists(self):
        """Test if the output file was created."""
        subprocess.run(['python', 'scripts/find-ranges-for-alignments.py', 'sample_ingestion_file.jsonl'], capture_output=True)
        self.assertTrue(os.path.exists(self.output_filename))

    def test_output_file_content(self):
        """Test the content of the output file."""
        with open(self.output_filename, 'r') as file:
            lines = file.readlines()
            # Check if the file is not empty
            self.assertTrue(len(lines) > 0)
            
            # Check the first line as an example
            first_line = lines[0]
            data = json.loads(first_line)
            
            # Check if certain keys exist in the data
            self.assertIn('vref', data)
            self.assertIn('macula', data)
            self.assertIn('bsb', data)
            self.assertIn('target', data)
            
            # Add more assertions as needed based on your expected output

if __name__ == '__main__':
    unittest.main()
