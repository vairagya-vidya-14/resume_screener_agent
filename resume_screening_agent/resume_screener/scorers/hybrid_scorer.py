import os
import sys

# Ensure parent and current directories are in sys.path for Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
repo_root = os.path.dirname(parent_dir)

for path in [parent_dir, current_dir, repo_root]:
    if path and path not in sys.path:
        sys.path.insert(0, path)

import json
import re
from typing import Dict, Any, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from resume_screener.extractors.entity_extractor import EntityExtractor
except ModuleNotFoundError:
    from extractors.entity_extractor import EntityExtractor

class HybridScorer:
    """
    Hybrid Resume Scoring Engine combining TF-IDF NLP vector similarity,
    skill coverage matrix matching, experience alignment, and structured LLM evaluation.
    """

    def __init__(self, api_key: Optional[str] = None, provider: str = "auto"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.provider = provider

    def evaluate_resume(
        self,
        resume_text: str,
        jd_text: str,
        resume_entities: Dict[str, Any],
        jd_entities: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a candidate resume against a job description.
        """
        if not jd_entities:
            jd_entities = EntityExtractor.extract_entities(jd_text, filename="job_description")

        # 1. Compute Scaled TF-IDF Cosine Similarity
        tfidf_score = self.compute_tfidf_similarity(resume_text, jd_text)

        # 2. Compute Skill Coverage Score
        skill_analysis = self.compute_skill_coverage(resume_entities.get("skills", []), jd_entities.get("skills", []))

        # 3. Compute Experience & Education Alignment Score
        exp_edu_score = self.compute_experience_education_score(
            resume_entities, jd_entities, jd_text
        )

        # 4. Compute Calibrated Deterministic NLP Score
        nlp_score = round(
            (0.35 * tfidf_score) +
            (0.45 * skill_analysis["coverage_ratio"]) +
            (0.20 * exp_edu_score),
            2
        )

        # 5. LLM Semantic Scoring (if API key available)
        llm_result = self.compute_llm_score(resume_text, jd_text, nlp_score, skill_analysis)

        if llm_result and "overall_score" in llm_result:
            llm_score = float(llm_result["overall_score"])
            final_score = round((0.40 * nlp_score) + (0.60 * llm_score), 2)
            eval_mode = f"Hybrid (NLP {40}% + LLM {60}%)"
        else:
            final_score = nlp_score
            llm_score = None
            eval_mode = "Deterministic NLP Fallback (No API Key)"
            llm_result = self._generate_fallback_reasoning(
                final_score, skill_analysis, exp_edu_score, resume_entities, jd_entities
            )

        return {
            "final_score": final_score,
            "evaluation_mode": eval_mode,
            "nlp_score": nlp_score,
            "tfidf_similarity": tfidf_score,
            "skill_coverage_score": skill_analysis["coverage_ratio"],
            "matched_skills": skill_analysis["matched_skills"],
            "missing_skills": skill_analysis["missing_skills"],
            "experience_education_score": exp_edu_score,
            "llm_score": llm_score,
            "strengths": llm_result.get("strengths", []),
            "gaps": llm_result.get("gaps", []),
            "reasoning": llm_result.get("reasoning", "Candidate evaluated based on skill matrix and document similarity."),
            "recommendation": self._get_recommendation_tier(final_score)
        }

    @staticmethod
    def compute_tfidf_similarity(resume_text: str, jd_text: str) -> float:
        """
        Computes TF-IDF cosine similarity between resume and job description.
        Scales raw document vector similarity (typically 0.10 - 0.35) into a 0 - 100 benchmark score.
        """
        if not resume_text or not jd_text:
            return 0.0
        try:
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
            raw_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            scaled = min(100.0, (raw_sim / 0.30) * 100.0)
            return round(scaled, 2)
        except Exception:
            return 0.0

    @staticmethod
    def compute_skill_coverage(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, Any]:
        """Calculates skill match coverage ratio and skill overlap lists."""
        if not jd_skills:
            return {
                "coverage_ratio": 80.0,
                "matched_skills": resume_skills,
                "missing_skills": []
            }

        resume_skills_lower = {s.lower(): s for s in resume_skills}
        matched = []
        missing = []

        for skill in jd_skills:
            if skill.lower() in resume_skills_lower:
                matched.append(skill)
            else:
                missing.append(skill)

        ratio = (len(matched) / len(jd_skills)) * 100.0 if jd_skills else 100.0
        return {
            "coverage_ratio": round(ratio, 2),
            "matched_skills": matched,
            "missing_skills": missing
        }

    @staticmethod
    def compute_experience_education_score(
        resume_entities: Dict[str, Any],
        jd_entities: Dict[str, Any],
        jd_text: str
    ) -> float:
        """Evaluates experience years and degree level match."""
        score = 70.0  # Base line

        # Experience matching
        res_exp = resume_entities.get("experience_years", 0.0)
        jd_exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', jd_text, re.IGNORECASE)
        req_exp = float(jd_exp_match.group(1)) if jd_exp_match else 3.0

        if res_exp >= req_exp:
            score += 15.0
        elif res_exp >= req_exp * 0.7:
            score += 5.0
        else:
            score -= 15.0

        # Education matching
        res_edu = resume_entities.get("education", [])
        if any(deg in ['PhD', 'Master\'s'] for deg in res_edu):
            score += 15.0
        elif 'Bachelor\'s' in res_edu:
            score += 10.0

        return min(max(round(score, 2), 0.0), 100.0)

    def compute_llm_score(
        self,
        resume_text: str,
        jd_text: str,
        nlp_score: float,
        skill_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Calls available LLM API (Groq, OpenAI) to return structured qualitative JSON score."""
        if not self.api_key:
            return None

        prompt = f"""
You are an expert HR Research Associate and Talent Acquisition AI.
Evaluate the following Candidate Resume against the Job Description.

Job Description:
\"\"\"
{jd_text[:3000]}
\"\"\"

Candidate Resume:
\"\"\"
{resume_text[:3000]}
\"\"\"

Preliminary NLP Analysis:
- TF-IDF Keyword Match: {nlp_score}/100
- Matched Skills: {', '.join(skill_analysis['matched_skills'][:10])}
- Missing Skills: {', '.join(skill_analysis['missing_skills'][:10])}

Task:
Respond ONLY with a valid JSON object matching this schema:
{{
  "technical_fit_score": <number 0-100>,
  "experience_fit_score": <number 0-100>,
  "education_fit_score": <number 0-100>,
  "overall_score": <number 0-100>,
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "gaps": ["<gap 1>", "<gap 2>"],
  "reasoning": "<detailed 2-3 sentence hiring recommendation and reasoning>"
}}
"""
        try:
            # Try Groq API first
            if os.getenv("GROQ_API_KEY") or (self.provider == "groq" and self.api_key):
                import groq
                client = groq.Groq(api_key=os.getenv("GROQ_API_KEY") or self.api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)

            # Try OpenAI API
            if os.getenv("OPENAI_API_KEY") or (self.provider == "openai" and self.api_key):
                import openai
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY") or self.api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
        except Exception:
            pass

        return None

    @staticmethod
    def _generate_fallback_reasoning(
        score: float,
        skill_analysis: Dict[str, Any],
        exp_edu_score: float,
        resume_entities: Dict[str, Any],
        jd_entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates clear, structured fallback reasoning when LLM API is offline."""
        matched = skill_analysis["matched_skills"]
        missing = skill_analysis["missing_skills"]
        exp = resume_entities.get("experience_years", 0)
        edu = ", ".join(resume_entities.get("education", ["Not Specified"]))

        strengths = []
        if matched:
            strengths.append(f"Demonstrated proficiency in core skills: {', '.join(matched[:4])}")
        if exp > 0:
            strengths.append(f"Relevant professional experience (~{int(exp)} years)")
        if edu != "Not Specified":
            strengths.append(f"Holds degree qualification ({edu})")

        gaps = []
        if missing:
            gaps.append(f"Missing expected JD skill requirements: {', '.join(missing[:4])}")
        if exp < 2:
            gaps.append("Limited recorded professional industry experience")

        reasoning = (
            f"Candidate achieved a composite score of {score}/100. "
            f"Matches {len(matched)} required skills with {exp} years of experience and {edu} qualification. "
            f"{'Strong candidate for interview shortlisting.' if score >= 70 else 'Good candidate with solid alignment.' if score >= 55 else 'Potential match needing technical verification.' if score >= 40 else 'Low alignment with core JD requirements.'}"
        )

        return {
            "strengths": strengths if strengths else ["Basic profile alignment"],
            "gaps": gaps if gaps else ["No major skill gaps identified"],
            "reasoning": reasoning
        }

    @staticmethod
    def _get_recommendation_tier(score: float) -> str:
        if score >= 70:
            return "Strong Match (Shortlist - Priority 1)"
        elif score >= 55:
            return "Good Match (Shortlist - Priority 2)"
        elif score >= 40:
            return "Potential Match (Secondary Review)"
        else:
            return "Unsuited (Reject / Hold)"
