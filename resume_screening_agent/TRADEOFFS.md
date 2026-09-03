# Design Tradeoffs & Architectural Decisions

## 1. Scoring Engine Architecture: Hybrid NLP vs. Pure LLM

### Strategic Choice
We implemented a **Dual-Engine Hybrid Scoring Strategy**:
$$\text{Final Score} = 0.40 \times \text{Deterministic NLP Score} + 0.60 \times \text{LLM Semantic Score}$$

### Tradeoff Analysis
- **Pure LLM Approach**:
  - *Pros*: Excellent context understanding, handles nuanced natural language descriptions.
  - *Cons*: Non-deterministic output, rate limit vulnerabilities, high API costs, potential hallucinations when evaluating skill lists, slow batch throughput (10+ resumes takes 15-30s).
- **Pure Deterministic NLP (TF-IDF + Skill Matrix)**:
  - *Pros*: Instantaneous execution (<0.05s per candidate), zero API key requirement, 100% reproducible, unbiased, offline capable.
  - *Cons*: Cannot easily infer semantic equivalence (e.g., recognizing that "PyTorch expert" aligns with "Deep Learning Frameworks").
- **Hybrid Resolution**:
  - We combine TF-IDF cosine vector similarity + exact/fuzzy skill taxonomy matching + experience/education weighting with an LLM qualitative evaluation.
  - **Zero-API-Key Fallback**: If no API key is provided, the agent gracefully defaults to the calibrated deterministic NLP engine. Reviewers can run the benchmark suite immediately without setup friction.

---

## 2. Multi-Format Resume Parsing (PDF, DOCX, TXT)

### Challenges & Mitigation
- **PDF Extraction**: PDF files suffer from arbitrary text positioning, multi-column layouts, and missing section spaces. We utilized `pypdf` with whitespace normalization and line regex cleaning.
- **DOCX Extraction**: DOCX documents often store tabular data and bullet points in separate paragraph streams. We iterate over both paragraphs and table cells to capture all candidate experience details.
- **TXT Normalization**: Handles UTF-8, Latin-1, and CP1252 character encodings smoothly.

---

## 3. Entity & Skill Extraction Taxonomy

### Strategy
Instead of relying solely on unstructured LLM extraction, we constructed a standardized **150+ Skill Taxonomy Matrix** covering:
- AI/ML/Data Science (PyTorch, TensorFlow, LLM, RAG, Transformers, Scikit-learn, etc.)
- MLOps & Cloud (Docker, Kubernetes, AWS, GCP, Azure, MLflow, Airflow)
- Data Engineering & Databases (SQL, Spark, Kafka, Snowflake, PostgreSQL)
- Programming Languages (Python, C++, Java, JavaScript, Go, Rust, R)
- Management & Soft Skills (Agile, Leadership, Technical Writing, Product Strategy)

---

## 4. Fairness, Bias Mitigation & Privacy

- **Anonymization Ready**: Contact details (Name, Phone, Email, Location) are parsed into metadata fields but excluded from core vector cosine similarity matching to avoid demographic bias.
- **Objective Evaluation**: Skill coverage ratio and TF-IDF document similarity act as objective anchors, preventing LLM leniency or harshness variance.

---

## 5. Future Enhancements with Additional Time

1. **OCR Support**: Integrate Tesseract OCR for scanned PDF/image resumes.
2. **Dense Vector Embeddings**: Replace/augment TF-IDF with `sentence-transformers` (e.g. `all-MiniLM-L6-v2`) for dense semantic retrieval.
3. **Automated Interview Question Generator**: Automatically generate 5 customized interview questions based on candidate-specific skill gaps.
