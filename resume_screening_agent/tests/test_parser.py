import os
import tempfile
import unittest
from resume_screener.parsers.resume_parser import ResumeParser

class TestResumeParser(unittest.TestCase):

    def setUp(self):
        self.sample_txt = os.path.join("data", "sample_resumes", "candidate_04_priya_sharma.txt")
        self.sample_pdf = os.path.join("data", "sample_resumes", "candidate_01_alex_chen.pdf")
        self.sample_docx = os.path.join("data", "sample_resumes", "candidate_02_sarah_jenkins.docx")

    def test_parse_txt(self):
        result = ResumeParser.parse_file(self.sample_txt)
        self.assertEqual(result["format"], "TXT")
        self.assertIn("Priya Sharma", result["clean_text"])
        self.assertGreater(result["word_count"], 20)

    def test_parse_pdf(self):
        result = ResumeParser.parse_file(self.sample_pdf)
        self.assertEqual(result["format"], "PDF")
        self.assertIn("Alex Chen", result["clean_text"])
        self.assertGreater(result["word_count"], 20)

    def test_parse_docx(self):
        result = ResumeParser.parse_file(self.sample_docx)
        self.assertEqual(result["format"], "DOCX")
        self.assertIn("Sarah Jenkins", result["clean_text"])
        self.assertGreater(result["word_count"], 20)

    def test_unsupported_format(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp:
            tmp.write(b"Dummy content")
            tmp_path = tmp.name
        try:
            with self.assertRaises(ValueError):
                ResumeParser.parse_file(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

if __name__ == "__main__":
    unittest.main()
