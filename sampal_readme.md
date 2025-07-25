# 🧠 AI-Powered Applicant Tracking System (CV + JD Matching)

This project is an intelligent, NLP-driven Applicant Tracking System that automates the process of matching **resumes (CVs)** to **job descriptions (JDs)**. It helps recruiters identify the **best-fit candidates** efficiently using machine learning techniques.

---

## 🔍 Key Features

- Upload Job Descriptions and multiple Resumes
- Automatically extract and process textual content
- Match resumes to job descriptions using:
  - ✅ TF-IDF + Cosine Similarity (fast and interpretable)
  - ✅ BERT embeddings (for deeper semantic understanding)
- Rank candidates based on similarity score
- Optional highlight of matched keywords and phrases
- User-friendly web portal for HR/admin use

---

## 📊 Model Options

| Model Type | Description | Libraries |
|------------|-------------|-----------|
| TF-IDF + Cosine Similarity | Lightweight, interpretable, suitable for MVPs | `scikit-learn`, `nltk` |
| BERT / Sentence-BERT (sBERT) | Context-aware, better accuracy | `transformers`, `sentence-transformers` |

---

## 📁 Dataset

You can use any collection of resumes and job descriptions in `.txt`, `.pdf`, or `.docx` format. For testing, the system supports:
- Synthetic or anonymized resumes
- Example job roles such as "Software Engineer", "Marketing Analyst", etc.

Folder structure:
project/
│
├── job_descriptions/
│ └── jd1.txt
├── resumes/
│ ├── resume1.txt
│ ├── resume2.txt
│ └── ...

