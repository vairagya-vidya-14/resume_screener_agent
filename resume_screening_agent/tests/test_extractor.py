import unittest
from resume_screener.extractors.entity_extractor import EntityExtractor

class TestEntityExtractor(unittest.TestCase):

    def test_extract_skills(self):
        text = "Experienced in Python, PyTorch, Docker, Kubernetes, AWS, and SQL."
        entities = EntityExtractor.extract_entities(text)
        skills = entities["skills"]
        self.assertIn("Python", skills)
        self.assertIn("PyTorch", skills)
        self.assertIn("Docker", skills)
        self.assertIn("SQL", skills)

    def test_extract_education(self):
        text = "Holds a Master of Science in Computer Science and a Bachelor of Engineering."
        entities = EntityExtractor.extract_entities(text)
        edu = entities["education"]
        self.assertIn("Master's", edu)
        self.assertIn("Bachelor's", edu)

    def test_extract_experience(self):
        text = "Over 6 years of experience working as a Machine Learning Engineer."
        entities = EntityExtractor.extract_entities(text)
        self.assertEqual(entities["experience_years"], 6.0)

    def test_extract_contact_info(self):
        text = "Alex Chen | Email: alex.chen@tech.com | Phone: +1-555-019-2834 | linkedin.com/in/alex-chen"
        entities = EntityExtractor.extract_entities(text)
        self.assertEqual(entities["email"], "alex.chen@tech.com")
        self.assertIn("linkedin.com/in/alex-chen", entities["linkedin"])

if __name__ == "__main__":
    unittest.main()
