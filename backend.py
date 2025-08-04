from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import shutil
from typing import List, Dict, Optional
import json
from pydantic import BaseModel
from resumematcher import ResumeMatcher

app = FastAPI(title="AI-Powered Applicant Tracking System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the resume matcher
matcher = ResumeMatcher(model_type="tfidf")

# Store uploaded resumes in memory (in production, use a database)
uploaded_resumes = []
uploaded_job_descriptions = []

# Request models
class MatchRequest(BaseModel):
    job_description_id: int

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI-Powered Applicant Tracking System API"}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and process a resume file.
    
    Args:
        file: Resume file (PDF, DOCX, or TXT)
        
    Returns:
        Processed resume data
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Extract text from file
            raw_text = matcher.extract_text_from_file(temp_file_path)
            
            if not raw_text:
                raise HTTPException(
                    status_code=400, 
                    detail="Could not extract text from the uploaded file"
                )
            
            # Clean text
            cleaned_text = matcher.clean_text(raw_text)
            
            # Extract candidate information
            candidate_info = matcher.extract_candidate_info(raw_text)
            
            # Create resume data
            resume_data = {
                'id': len(uploaded_resumes) + 1,
                'file_name': file.filename,
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'candidate_name': candidate_info['candidate_name'],
                'email': candidate_info['email'],
                'phone': candidate_info['phone'],
                'experience_years': candidate_info['experience_years'],
                'skills': candidate_info['skills'],
                'education': candidate_info['education'],
                'file_size': file.size
            }
            
            # Add to uploaded resumes
            uploaded_resumes.append(resume_data)
            
            # Add to matcher's resume texts
            matcher.resume_texts.append(cleaned_text)
            
            return {
                "success": True,
                "message": "Resume uploaded and processed successfully",
                "resume": resume_data
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@app.post("/upload-job-description")
async def upload_job_description(
    title: str = Form(...),
    description: str = Form(...),
    requirements: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    experience_level: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    salary_range: Optional[str] = Form(None)
):
    """
    Upload a job description.
    
    Args:
        title: Job title
        description: Job description
        requirements: Job requirements (optional)
        skills: Required skills (optional)
        experience_level: Experience level (optional)
        location: Job location (optional)
        salary_range: Salary range (optional)
        
    Returns:
        Created job description data
    """
    try:
        # Parse skills if provided
        skills_list = []
        if skills:
            skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
        
        # Create job description data
        jd_data = {
            'id': len(uploaded_job_descriptions) + 1,
            'title': title,
            'description': description,
            'requirements': requirements,
            'skills': skills_list,
            'experience_level': experience_level,
            'location': location,
            'salary_range': salary_range
        }
        
        # Add to uploaded job descriptions
        uploaded_job_descriptions.append(jd_data)
        
        return {
            "success": True,
            "message": "Job description uploaded successfully",
            "job_description": jd_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading job description: {str(e)}")

@app.get("/resumes")
async def get_resumes():
    """Get all uploaded resumes."""
    return {
        "success": True,
        "resumes": uploaded_resumes
    }

@app.get("/job-descriptions")
async def get_job_descriptions():
    """Get all uploaded job descriptions."""
    return {
        "success": True,
        "job_descriptions": uploaded_job_descriptions
    }

@app.post("/match")
async def match_resumes(request: MatchRequest):
    """
    Match resumes to a specific job description.
    
    Args:
        request: MatchRequest containing job_description_id
        
    Returns:
        Matching results
    """
    try:
        job_description_id = request.job_description_id
        
        # Find the job description
        jd = None
        for job_desc in uploaded_job_descriptions:
            if job_desc['id'] == job_description_id:
                jd = job_desc
                break
        
        if not jd:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        if not uploaded_resumes:
            raise HTTPException(status_code=400, detail="No resumes uploaded")
        
        # Perform matching
        full_description = f"{jd['title']} {jd['description']}"
        if jd['requirements']:
            full_description += f" {jd['requirements']}"
        if jd['skills']:
            full_description += f" {' '.join(jd['skills'])}"
        
        results = matcher.match_resumes(full_description, uploaded_resumes, top_k=10)
        
        # Format results for API response
        formatted_results = []
        for result in results:
            resume = result['resume']
            formatted_result = {
                'resume_id': resume['id'],
                'candidate_name': resume['candidate_name'],
                'email': resume['email'],
                'file_name': resume['file_name'],
                'experience_years': resume['experience_years'],
                'skills': resume['skills'],
                'education': resume['education'],
                'similarity_score': result['similarity_score'],
                'matched_skills': result['matched_skills'],
                'highlights': result['highlights'],
                'rank': result['rank']
            }
            formatted_results.append(formatted_result)
        
        return {
            "success": True,
            "job_description": jd,
            "total_candidates": len(uploaded_resumes),
            "matched_candidates": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing matching: {str(e)}")

@app.post("/match-all")
async def match_all_resumes():
    """
    Match all resumes to all job descriptions.
    
    Returns:
        All matching results
    """
    try:
        if not uploaded_job_descriptions:
            raise HTTPException(status_code=400, detail="No job descriptions uploaded")
        
        if not uploaded_resumes:
            raise HTTPException(status_code=400, detail="No resumes uploaded")
        
        all_results = {}
        
        for jd in uploaded_job_descriptions:
            full_description = f"{jd['title']} {jd['description']}"
            if jd['requirements']:
                full_description += f" {jd['requirements']}"
            if jd['skills']:
                full_description += f" {' '.join(jd['skills'])}"
            
            results = matcher.match_resumes(full_description, uploaded_resumes, top_k=5)
            
            formatted_results = []
            for result in results:
                resume = result['resume']
                formatted_result = {
                    'resume_id': resume['id'],
                    'candidate_name': resume['candidate_name'],
                    'email': resume['email'],
                    'file_name': resume['file_name'],
                    'experience_years': resume['experience_years'],
                    'skills': resume['skills'],
                    'education': resume['education'],
                    'similarity_score': result['similarity_score'],
                    'matched_skills': result['matched_skills'],
                    'highlights': result['highlights'],
                    'rank': result['rank']
                }
                formatted_results.append(formatted_result)
            
            all_results[jd['id']] = {
                'job_description': jd,
                'results': formatted_results
            }
        
        return {
            "success": True,
            "total_job_descriptions": len(uploaded_job_descriptions),
            "total_candidates": len(uploaded_resumes),
            "results": all_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing matching: {str(e)}")

@app.delete("/resume/{resume_id}")
async def delete_resume(resume_id: int):
    """
    Delete a resume by ID.
    
    Args:
        resume_id: ID of the resume to delete
        
    Returns:
        Success message
    """
    try:
        global uploaded_resumes
        
        # Find and remove the resume
        for i, resume in enumerate(uploaded_resumes):
            if resume['id'] == resume_id:
                # Remove from uploaded resumes
                uploaded_resumes.pop(i)
                
                # Remove from matcher's resume texts
                if i < len(matcher.resume_texts):
                    matcher.resume_texts.pop(i)
                
                return {
                    "success": True,
                    "message": f"Resume {resume_id} deleted successfully"
                }
        
        raise HTTPException(status_code=404, detail="Resume not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting resume: {str(e)}")

@app.delete("/job-description/{jd_id}")
async def delete_job_description(jd_id: int):
    """
    Delete a job description by ID.
    
    Args:
        jd_id: ID of the job description to delete
        
    Returns:
        Success message
    """
    try:
        global uploaded_job_descriptions
        
        # Find and remove the job description
        for i, jd in enumerate(uploaded_job_descriptions):
            if jd['id'] == jd_id:
                uploaded_job_descriptions.pop(i)
                return {
                    "success": True,
                    "message": f"Job description {jd_id} deleted successfully"
                }
        
        raise HTTPException(status_code=404, detail="Job description not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting job description: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    return {
        "success": True,
        "stats": {
            "total_resumes": len(uploaded_resumes),
            "total_job_descriptions": len(uploaded_job_descriptions),
            "model_type": matcher.model_type,
            "processed_resume_texts": len(matcher.resume_texts)
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 