import unittest
from resume_screener.scorers.hybrid_scorer import HybridScorer

class TestHybridScorer(unittest.TestCase):

    def setUp(self):
        self.scorer = HybridScorer()

    def test_tfidf_similarity(self):
        jd = "Seeking a Python PyTorch Machine Learning Engineer with Docker experience."
        resume_match = "Senior AI Engineer skilled in Python, PyTorch, Deep Learning, and Docker."
        resume_non_match = "Experienced Graphic Designer proficient in Photoshop, Illustrator, and Figma."

        score_match = self.scorer.compute_tfidf_similarity(resume_match, jd)
        score_non_match = self.scorer.compute_tfidf_similarity(resume_non_match, jd)

        self.assertGreater(score_match, score_non_match)

    def test_skill_coverage(self):
        resume_skills = ["Python", "PyTorch", "Docker", "AWS"]
        jd_skills = ["Python", "PyTorch", "Kubernetes", "AWS", "SQL"]

        analysis = self.scorer.compute_skill_coverage(resume_skills, jd_skills)
        self.assertIn("Python", analysis["matched_skills"])
        self.assertIn("Kubernetes", analysis["missing_skills"])
        self.assertEqual(len(analysis["matched_skills"]), 3)
        self.assertEqual(analysis["coverage_ratio"], 60.0)

if __name__ == "__main__":
    unittest.main()
