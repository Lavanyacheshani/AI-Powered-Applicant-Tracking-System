AI-Powered Resume-JD Matching System
--------------------------------------------------
This project matches job descriptions with resumes using BERT embeddings and cosine similarity.

Files Included:
- CleanedResumeDataSet.csv : Resume dataset cleaned and ready for inference
- requirements.txt : Python packages needed to run the model
- resume.py : Model and logic for matching (BERT-based)

Instructions:
1. Install dependencies:
   pip install -r requirements.txt

2. Load the CleanedResumeDataSet.csv using pandas

3. Use SentenceTransformer to encode resumes and JDs:
   from sentence_transformers import SentenceTransformer, util

4. Compute similarity scores and rank resumes for each JD.

Optional:
- Add JD input via file or user interface
- Build Streamlit/Flask web app for deployment

For help, contact the ML team.
