import os
import re
from typing import Dict, Any, List, Set

class EntityExtractor:
    """
    Extracts structured entities from resume text including candidate contact info,
    education level, years of experience, and technical/soft skills.
    """

    SKILL_TAXONOMY = {
        # AI / ML / Data Science
        "Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Keras", "Machine Learning", "Deep Learning",
        "Natural Language Processing", "NLP", "LLM", "Generative AI", "RAG", "LangChain", "LlamaIndex",
        "Transformers", "Hugging Face", "Computer Vision", "OpenCV", "BERT", "GPT", "Prompt Engineering",
        "Fine-tuning", "Reinforcement Learning", "Neural Networks", "Pandas", "NumPy", "SciPy", "Matplotlib",
        "Seaborn", "Statsmodels", "Data Analysis", "Feature Engineering", "Model Evaluation", "A/B Testing",

        # MLOps & Cloud / DevOps
        "MLOps", "Docker", "Kubernetes", "AWS", "GCP", "Azure", "MLflow", "Kubeflow", "Airflow", "CI/CD",
        "Git", "GitHub", "Linux", "Terraform", "FastAPI", "Flask", "Django", "REST API", "Microservices",

        # Data Engineering & Databases
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Apache Spark", "Hadoop", "PySpark", "Kafka",
        "Snowflake", "BigQuery", "Data Warehousing", "ETL", "Databricks",

        # Programming Languages & Web
        "C++", "C", "Java", "JavaScript", "TypeScript", "React", "Node.js", "HTML5", "CSS3", "HTML/CSS", "Go", "Rust", "R", "Julia",

        # Soft Skills & Management
        "Project Management", "Agile", "Scrum", "Leadership", "Team Collaboration", "Problem Solving",
        "Communication", "Research", "Technical Writing", "Product Strategy", "Cross-Functional Leadership"
    }

    EDUCATION_PATTERNS = [
        # PhD / Doctorate
        (r'\b(Ph\.?\s*D\.?|Doctorate|Doctor of Philosophy)\b', 'PhD'),
        
        # Master's / Post Graduate
        (r'\b(Master|Masters|Master\'s|M[\s\.]*Tech|M[\s\.]*S|M[\s\.]*E|M[\s\.]*A|M[\s\.]*C[\s\.]*A|MBA|PGDM|Post\s*Graduat\w*)\b', 'Master\'s'),
        
        # Bachelor's / Undergraduate
        (r'\b(Bachelor|Bachelors|Bachelor\'s|B[\s\.]*Tech|B[\s\.]*E|B[\s\.]*S|B[\s\.]*A|B[\s\.]*C[\s\.]*A|B[\s\.]*Com|BTech|BE|BSc|BCA|BCom|Undergraduat\w*)\b', 'Bachelor\'s'),
        
        # Diploma / Associate
        (r'\b(Diploma|Associate Degree|A\.?S|A\.?A)\b', 'Diploma / Associate'),
        
        # High School / Intermediate
        (r'\b(Intermediate|Class\s*12|12th|Class\s*10|10th|SSC|High\s*School)\b', 'High School / Intermediate')
    ]

    @classmethod
    def extract_entities(cls, text: str, filename: str = "") -> Dict[str, Any]:
        """
        Extracts structured entities from resume clean text.
        """
        email = cls._extract_email(text)
        phone = cls._extract_phone(text)
        name = cls._extract_candidate_name(text, filename)
        linkedin = cls._extract_linkedin(text)
        github = cls._extract_github(text)
        education = cls._extract_education(text)
        experience_years = cls._extract_experience_years(text)
        extracted_skills = cls._extract_skills(text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "education": education,
            "experience_years": experience_years,
            "skills": extracted_skills,
            "skill_count": len(extracted_skills)
        }

    @staticmethod
    def _extract_email(text: str) -> str:
        match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        return match.group(0) if match else "N/A"

    @staticmethod
    def _extract_phone(text: str) -> str:
        pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(pattern, text)
        return match.group(0) if match else "N/A"

    @staticmethod
    def _extract_linkedin(text: str) -> str:
        match = re.search(r'(https?://)?(www\.)?linkedin\.com/(in|pub|profile|company)/[a-zA-Z0-9_%-]+/?', text, re.IGNORECASE)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return url
        return "N/A"

    @staticmethod
    def _extract_github(text: str) -> str:
        matches = re.finditer(r'(https?://)?(www\.)?github\.com/([a-zA-Z0-9_-]+)/?', text, re.IGNORECASE)
        for match in matches:
            username = match.group(3)
            if username.lower() not in ["features", "pricing", "signup", "login", "about", "topics", "collections"]:
                url = match.group(0)
                if not url.startswith("http"):
                    url = "https://" + url
                return url
        return "N/A"

    @classmethod
    def _extract_candidate_name(cls, text: str, filename: str) -> str:
        if filename:
            clean_fname = re.sub(r'^candidate_\d+_', '', filename, flags=re.IGNORECASE)
            clean_fname = os.path.splitext(clean_fname)[0]
            clean_fname = clean_fname.replace('_', ' ').replace('-', ' ').title()
            if len(clean_fname.split()) >= 2 and clean_fname.lower() != "job description":
                return clean_fname

        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:3]:
            clean_line = re.sub(r'\(.*?\)', '', line)
            clean_line = re.sub(r'[^\w\s]', '', clean_line).strip()
            words = clean_line.split()
            if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                return clean_line.title()

        return "Candidate"

    @classmethod
    def _extract_education(cls, text: str) -> List[str]:
        text_clean = re.sub(r'\s+', ' ', text)
        found = []
        for pattern, degree in cls.EDUCATION_PATTERNS:
            if re.search(pattern, text_clean, re.IGNORECASE):
                if degree not in found:
                    found.append(degree)

        # Higher degree prioritization (PhD, Master's, Bachelor's) over High School
        higher = [d for d in found if d in ['PhD', 'Master\'s', 'Bachelor\'s']]
        if higher:
            return higher

        # Comprehensive fallback for University/College/Engineering/CGPA keywords
        if re.search(r'\b(JNTU|JNTUH|College|University|Engineering|CGPA|Percentage|B\.?Tech|BTech|B\.E|BE|BSc|Degree|Institute)\b', text_clean, re.IGNORECASE):
            return ["Bachelor's"]

        return found if found else ["Not Specified"]

    @classmethod
    def _extract_experience_years(cls, text: str) -> float:
        explicit_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:professional|work|industry)?\s*experience', text, re.IGNORECASE)
        if explicit_match:
            return float(explicit_match.group(1))

        if re.search(r'\b(undergraduate|fresher|student|entry-level|entry level)\b', text, re.IGNORECASE) and not re.search(r'\bwork experience\b|\bprofessional experience\b|\bemployment history\b', text, re.IGNORECASE):
            return 0.0

        exp_section_match = re.search(r'(?:work experience|professional experience|employment history)(.*?)(?:education|projects|certifications|skills|additional information|$)', text, re.IGNORECASE | re.DOTALL)
        search_text = exp_section_match.group(1) if exp_section_match else ""

        if search_text:
            years = re.findall(r'\b(20\d{2}|19\d{2})\b', search_text)
            if len(years) >= 2:
                int_years = [int(y) for y in years]
                min_year = min(int_years)
                max_year = max(int_years)
                current_year = 2026
                if "present" in search_text.lower() or "current" in search_text.lower():
                    max_year = current_year
                diff = max_year - min_year
                if 0 < diff <= 30:
                    return float(diff)

        return 0.0

    @classmethod
    def _extract_skills(cls, text: str) -> List[str]:
        found_skills = set()
        text_lower = text.lower()

        for skill in cls.SKILL_TAXONOMY:
            skill_lower = skill.lower()
            if len(skill) <= 4:
                pattern = r'\b' + re.escape(skill_lower) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(skill)
            else:
                if skill_lower in text_lower:
                    found_skills.add(skill)

        return sorted(list(found_skills))
