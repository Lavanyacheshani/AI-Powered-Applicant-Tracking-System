import pandas as pd
import numpy as np
import re
import json
import os
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
import PyPDF2
from docx import Document
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeMatcher:
    def __init__(self, model_type: str = "tfidf"):
        """
        Initialize the ResumeMatcher with specified model type.
        
        Args:
            model_type: "tfidf" or "bert"
        """
        self.model_type = model_type
        self.tfidf_vectorizer = None
        self.bert_model = None
        self.resume_embeddings = None
        self.resume_texts = []
        self.stop_words = set(stopwords.words('english'))
        
        if model_type == "bert":
            if BERT_AVAILABLE:
                try:
                    self.bert_model = SentenceTransformer('all-MiniLM-L6-v2')
                except Exception as e:
                    self.logger.warning(f"BERT model failed to load: {e}. Falling back to TF-IDF.")
                    self.model_type = "tfidf"
            else:
                self.logger.warning("BERT not available. Falling back to TF-IDF.")
                self.model_type = "tfidf"
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text for analysis.
        
        Args:
            text: Raw text input
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        
        # Remove numbers (optional - you might want to keep years)
        text = re.sub(r'\b\d+\b', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from various file formats.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text
        """
        file_extension = file_path.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['docx', 'doc']:
            return self.extract_text_from_docx(file_path)
        elif file_extension == 'txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except Exception as e:
                self.logger.error(f"Error reading text file {file_path}: {e}")
                return ""
        else:
            self.logger.warning(f"Unsupported file format: {file_extension}")
            return ""
    
    def extract_candidate_info(self, text: str) -> Dict:
        """
        Extract candidate information from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with candidate information
        """
        # Simple extraction - in a real system, you'd use more sophisticated NLP
        info = {
            'candidate_name': 'Unknown',
            'email': '',
            'phone': '',
            'experience_years': 0,
            'skills': [],
            'education': 'Not specified'
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            info['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            info['phone'] = ''.join(phones[0])
        
        # Extract skills (common programming/technical skills)
        skill_patterns = [
            r'\b(?:JavaScript|JS|React|Angular|Vue|Node\.js|Python|Java|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin)\b',
            r'\b(?:HTML|CSS|SASS|LESS|Bootstrap|Tailwind|jQuery|TypeScript)\b',
            r'\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Oracle|SQLite)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab)\b',
            r'\b(?:Machine Learning|ML|AI|Deep Learning|NLP|Computer Vision|TensorFlow|PyTorch|Scikit-learn)\b',
            r'\b(?:Agile|Scrum|Kanban|JIRA|Confluence|Slack|Microsoft Office|Excel|PowerPoint)\b'
        ]
        
        skills = []
        for pattern in skill_patterns:
            found_skills = re.findall(pattern, text, re.IGNORECASE)
            skills.extend(found_skills)
        
        info['skills'] = list(set(skills))
        
        # Extract experience years (simple pattern)
        exp_pattern = r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience'
        exp_match = re.search(exp_pattern, text, re.IGNORECASE)
        if exp_match:
            info['experience_years'] = int(exp_match.group(1))
        
        # Extract education
        education_patterns = [
            r'\b(?:Bachelor|Master|PhD|BSc|MSc|MBA|PhD)\b',
            r'\b(?:University|College|Institute|School)\b'
        ]
        
        for pattern in education_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                info['education'] = 'Higher Education'
                break
        
        return info
    
    def load_resumes_from_directory(self, directory_path: str) -> List[Dict]:
        """
        Load and process resumes from a directory.
        
        Args:
            directory_path: Path to directory containing resume files
            
        Returns:
            List of processed resume dictionaries
        """
        resumes = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                # Extract text from file
                raw_text = self.extract_text_from_file(file_path)
                
                if raw_text:
                    # Clean text
                    cleaned_text = self.clean_text(raw_text)
                    
                    # Extract candidate information
                    candidate_info = self.extract_candidate_info(raw_text)
                    
                    resume_data = {
                        'file_name': filename,
                        'raw_text': raw_text,
                        'cleaned_text': cleaned_text,
                        'candidate_name': candidate_info['candidate_name'],
                        'email': candidate_info['email'],
                        'phone': candidate_info['phone'],
                        'experience_years': candidate_info['experience_years'],
                        'skills': candidate_info['skills'],
                        'education': candidate_info['education']
                    }
                    
                    resumes.append(resume_data)
                    self.resume_texts.append(cleaned_text)
        
        return resumes
    
    def prepare_tfidf_model(self):
        """Prepare TF-IDF vectorizer with resume texts."""
        if not self.resume_texts:
            raise ValueError("No resume texts available. Load resumes first.")
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Fit the vectorizer on resume texts
        self.tfidf_vectorizer.fit(self.resume_texts)
    
    def prepare_bert_model(self):
        """Prepare BERT embeddings for resumes."""
        if not self.resume_texts:
            raise ValueError("No resume texts available. Load resumes first.")
        
        # Encode all resume texts
        self.resume_embeddings = self.bert_model.encode(
            self.resume_texts, 
            convert_to_tensor=True
        )
    
    def match_tfidf(self, job_description: str, top_k: int = 5) -> List[Dict]:
        """
        Match job description to resumes using TF-IDF and cosine similarity.
        
        Args:
            job_description: Job description text
            top_k: Number of top matches to return
            
        Returns:
            List of match results with scores and resume data
        """
        if not self.tfidf_vectorizer:
            self.prepare_tfidf_model()
        
        # Clean job description
        cleaned_jd = self.clean_text(job_description)
        
        # Transform job description
        jd_vector = self.tfidf_vectorizer.transform([cleaned_jd])
        
        # Transform resume texts
        resume_vectors = self.tfidf_vectorizer.transform(self.resume_texts)
        
        # Calculate cosine similarities
        similarities = cosine_similarity(jd_vector, resume_vectors).flatten()
        
        # Get top matches
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'resume_index': idx,
                'similarity_score': float(similarities[idx]),
                'percentage_score': float(similarities[idx] * 100)
            })
        
        return results
    
    def match_bert(self, job_description: str, top_k: int = 5) -> List[Dict]:
        """
        Match job description to resumes using BERT embeddings.
        
        Args:
            job_description: Job description text
            top_k: Number of top matches to return
            
        Returns:
            List of match results with scores and resume data
        """
        if not self.resume_embeddings:
            self.prepare_bert_model()
        
        # Clean job description
        cleaned_jd = self.clean_text(job_description)
        
        # Encode job description
        jd_embedding = self.bert_model.encode(cleaned_jd, convert_to_tensor=True)
        
        # Calculate cosine similarities
        cosine_scores = util.pytorch_cos_sim(jd_embedding, self.resume_embeddings)[0]
        
        # Get top matches
        top_results = torch.topk(cosine_scores, k=min(top_k, len(cosine_scores)))
        
        results = []
        for score, idx in zip(top_results[0], top_results[1]):
            results.append({
                'resume_index': idx.item(),
                'similarity_score': float(score),
                'percentage_score': float(score * 100)
            })
        
        return results
    
    def find_matched_skills(self, job_description: str, resume_skills: List[str]) -> List[str]:
        """
        Find skills that match between job description and resume.
        
        Args:
            job_description: Job description text
            resume_skills: List of skills from resume
            
        Returns:
            List of matched skills
        """
        cleaned_jd = self.clean_text(job_description).lower()
        matched_skills = []
        
        for skill in resume_skills:
            skill_lower = skill.lower()
            if skill_lower in cleaned_jd:
                matched_skills.append(skill)
        
        return matched_skills
    
    def match_resumes(self, job_description: str, resumes: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Match job description to resumes using the specified model.
        
        Args:
            job_description: Job description text
            resumes: List of resume dictionaries
            top_k: Number of top matches to return
            
        Returns:
            List of match results with detailed information
        """
        # Load resume texts if not already loaded
        if not self.resume_texts:
            self.resume_texts = [resume['cleaned_text'] for resume in resumes]
        
        # Perform matching based on model type
        if self.model_type == "tfidf":
            match_results = self.match_tfidf(job_description, top_k)
        else:  # bert
            match_results = self.match_bert(job_description, top_k)
        
        # Enhance results with resume data and additional analysis
        enhanced_results = []
        for result in match_results:
            resume_idx = result['resume_index']
            resume = resumes[resume_idx]
            
            # Find matched skills
            matched_skills = self.find_matched_skills(job_description, resume['skills'])
            
            # Create highlights
            highlights = [
                f"{resume['experience_years']} years of experience",
                f"{len(matched_skills)} matching skills",
                resume['education']
            ]
            
            enhanced_result = {
                'resume': resume,
                'similarity_score': result['percentage_score'],
                'matched_skills': matched_skills,
                'highlights': highlights,
                'rank': len(enhanced_results) + 1
            }
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def save_results(self, results: List[Dict], output_file: str):
        """
        Save matching results to a file.
        
        Args:
            results: List of match results
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {output_file}")

def main():
    """Example usage of the ResumeMatcher class."""
    
    # Initialize matcher with BERT model
    matcher = ResumeMatcher(model_type="bert")
    
    # Example job descriptions
    job_descriptions = [
        {
            "title": "Senior Software Engineer",
            "description": """
            We are looking for a Senior Software Engineer with strong experience in:
            - JavaScript, React, Node.js
            - Python and machine learning
            - AWS cloud services
            - 5+ years of experience
            - Bachelor's degree in Computer Science
            """
        },
        {
            "title": "Data Scientist",
            "description": """
            Join our data science team! Requirements:
            - Python, pandas, scikit-learn
            - Machine learning and statistical analysis
            - SQL and data visualization
            - 3+ years of experience
            - Master's degree preferred
            """
        }
    ]
    
    # Load resumes from directory (if available)
    resumes_dir = "resumes"
    if os.path.exists(resumes_dir):
        resumes = matcher.load_resumes_from_directory(resumes_dir)
        
        for i, jd in enumerate(job_descriptions):
            print(f"\n{'='*50}")
            print(f"Job: {jd['title']}")
            print(f"{'='*50}")
            
            results = matcher.match_resumes(jd['description'], resumes, top_k=3)
            
            for result in results:
                resume = result['resume']
                print(f"\nRank #{result['rank']}")
                print(f"Score: {result['similarity_score']:.2f}%")
                print(f"Candidate: {resume['candidate_name']}")
                print(f"Email: {resume['email']}")
                print(f"Experience: {resume['experience_years']} years")
                print(f"Skills: {', '.join(resume['skills'])}")
                print(f"Matched Skills: {', '.join(result['matched_skills'])}")
                print(f"Highlights: {', '.join(result['highlights'])}")
    else:
        print(f"Resumes directory '{resumes_dir}' not found. Please add resume files to test the system.")

if __name__ == "__main__":
    main()