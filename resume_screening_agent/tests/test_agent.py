import os
import unittest
from resume_screener.agent import ResumeScreeningAgent

class TestResumeScreeningAgent(unittest.TestCase):

    def test_screen_resumes_folder(self):
        agent = ResumeScreeningAgent()
        jd_path = os.path.join("data", "sample_jds", "senior_ai_engineer.txt")
        resume_dir = os.path.join("data", "sample_resumes")
        output_dir = os.path.join("outputs", "test_outputs")

        results = agent.screen_resumes_folder(resume_dir, jd_path, output_dir=output_dir)

        self.assertEqual(results["total_candidates"], 13)
        self.assertGreater(len(results["ranked_candidates"]), 0)
        self.assertTrue(os.path.exists(results["outputs"]["json"]))
        self.assertTrue(os.path.exists(results["outputs"]["csv"]))

if __name__ == "__main__":
    unittest.main()
