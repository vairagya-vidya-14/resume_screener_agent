import os
import sys

# Ensure parent and current directories are in sys.path for Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
repo_root = os.path.dirname(parent_dir)

for path in [current_dir, parent_dir, repo_root]:
    if path and path not in sys.path:
        sys.path.insert(0, path)

import json
import pandas as pd
from typing import Dict, Any, List, Optional

try:
    from parsers.resume_parser import ResumeParser
    from extractors.entity_extractor import EntityExtractor
    from scorers.hybrid_scorer import HybridScorer
except (ImportError, ModuleNotFoundError):
    from resume_screener.parsers.resume_parser import ResumeParser
    from resume_screener.extractors.entity_extractor import EntityExtractor
    from resume_screener.scorers.hybrid_scorer import HybridScorer

class ResumeScreeningAgent:
    """
    Core AI Resume Screening Agent that handles batch resume parsing, entity extraction,
    hybrid NLP/LLM scoring against job descriptions, candidate ranking, and output generation.
    """

    def __init__(self, api_key: Optional[str] = None, provider: str = "auto"):
        self.parser = ResumeParser()
        self.extractor = EntityExtractor()
        self.scorer = HybridScorer(api_key=api_key, provider=provider)

    def screen_resumes_folder(
        self,
        resume_folder_path: str,
        jd_path_or_text: str,
        output_dir: str = "outputs"
    ) -> Dict[str, Any]:
        """
        Processes a directory of resumes against a Job Description.
        """
        if not os.path.exists(resume_folder_path):
            raise FileNotFoundError(f"Resume directory not found: {resume_folder_path}")

        # Load Job Description Text
        jd_text = self._load_jd_text(jd_path_or_text)
        jd_entities = self.extractor.extract_entities(jd_text, filename="Job Description")

        # Collect resume files
        files = [
            os.path.join(resume_folder_path, f) for f in os.listdir(resume_folder_path)
            if os.path.splitext(f)[1].lower() in ResumeParser.SUPPORTED_EXTENSIONS
        ]

        if not files:
            raise ValueError(f"No supported resume files (.pdf, .docx, .txt) found in {resume_folder_path}")

        return self.screen_resume_files(files, jd_text, jd_entities, output_dir=output_dir)

    def screen_resume_files(
        self,
        file_paths: List[str],
        jd_text: str,
        jd_entities: Optional[Dict[str, Any]] = None,
        output_dir: str = "outputs"
    ) -> Dict[str, Any]:
        """
        Processes a list of resume file paths against JD text.
        """
        if not jd_entities:
            jd_entities = self.extractor.extract_entities(jd_text, filename="Job Description")

        candidate_results = []

        for file_path in file_paths:
            try:
                parsed = self.parser.parse_file(file_path)
                entities = self.extractor.extract_entities(parsed["clean_text"], filename=parsed["filename"])
                eval_result = self.scorer.evaluate_resume(
                    resume_text=parsed["clean_text"],
                    jd_text=jd_text,
                    resume_entities=entities,
                    jd_entities=jd_entities
                )

                candidate_record = {
                    "filename": parsed["filename"],
                    "format": parsed["format"],
                    "candidate_name": entities["name"],
                    "email": entities["email"],
                    "phone": entities["phone"],
                    "linkedin": entities["linkedin"],
                    "github": entities["github"],
                    "education": entities["education"],
                    "experience_years": entities["experience_years"],
                    "skills": entities["skills"],
                    "final_score": eval_result["final_score"],
                    "evaluation_mode": eval_result["evaluation_mode"],
                    "nlp_score": eval_result["nlp_score"],
                    "tfidf_similarity": eval_result["tfidf_similarity"],
                    "skill_coverage_score": eval_result["skill_coverage_score"],
                    "matched_skills": eval_result["matched_skills"],
                    "missing_skills": eval_result["missing_skills"],
                    "experience_education_score": eval_result["experience_education_score"],
                    "llm_score": eval_result["llm_score"],
                    "recommendation": eval_result["recommendation"],
                    "strengths": eval_result["strengths"],
                    "gaps": eval_result["gaps"],
                    "reasoning": eval_result["reasoning"]
                }
                candidate_results.append(candidate_record)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

        # Rank candidates by final score descending
        candidate_results.sort(key=lambda x: x["final_score"], reverse=True)
        for rank, cand in enumerate(candidate_results, 1):
            cand["rank"] = rank

        # Generate outputs
        os.makedirs(output_dir, exist_ok=True)
        json_output_path = os.path.join(output_dir, "ranked_candidates.json")
        csv_output_path = os.path.join(output_dir, "ranked_candidates.csv")

        self._export_json(candidate_results, jd_entities, json_output_path)
        self._export_csv(candidate_results, csv_output_path)

        avg_score = round(sum(c["final_score"] for c in candidate_results) / len(candidate_results), 2) if candidate_results else 0.0

        return {
            "total_candidates": len(candidate_results),
            "job_description_required_skills": jd_entities.get("skills", []),
            "average_score": avg_score,
            "top_candidate": candidate_results[0] if candidate_results else None,
            "ranked_candidates": candidate_results,
            "outputs": {
                "json": os.path.abspath(json_output_path),
                "csv": os.path.abspath(csv_output_path)
            }
        }

    @staticmethod
    def _load_jd_text(jd_path_or_text: str) -> str:
        if os.path.exists(jd_path_or_text):
            return ResumeParser.parse_file(jd_path_or_text)["clean_text"]
        return jd_path_or_text.strip()

    @staticmethod
    def _export_json(results: List[Dict[str, Any]], jd_entities: Dict[str, Any], filepath: str):
        payload = {
            "metadata": {
                "agent": "AI Resume Screening Agent",
                "version": "1.0.0",
                "total_candidates": len(results),
                "jd_required_skills": jd_entities.get("skills", [])
            },
            "rankings": results
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    @staticmethod
    def _export_csv(results: List[Dict[str, Any]], filepath: str):
        flat_records = []
        for c in results:
            flat_records.append({
                "Rank": c["rank"],
                "Candidate Name": c["candidate_name"],
                "Final Score": c["final_score"],
                "Recommendation": c["recommendation"],
                "Filename": c["filename"],
                "Format": c["format"],
                "Experience (Yrs)": c["experience_years"],
                "Education": ", ".join(c["education"]),
                "Email": c["email"],
                "Phone": c["phone"],
                "Matched Skills Count": len(c["matched_skills"]),
                "Matched Skills": "; ".join(c["matched_skills"]),
                "Missing Skills": "; ".join(c["missing_skills"]),
                "TFIDF Sim (%)": c["tfidf_similarity"],
                "Reasoning": c["reasoning"]
            })
        df = pd.DataFrame(flat_records)
        df.to_csv(filepath, index=False, encoding="utf-8")
