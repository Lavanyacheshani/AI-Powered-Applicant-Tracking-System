#!/usr/bin/env python3
"""
Test script for the AI-Powered Applicant Tracking System
"""

import requests
import json
import time
import os

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test if the backend is running and healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start the backend first.")
        return False

def test_job_description_upload():
    """Test job description upload."""
    try:
        job_data = {
            "title": "Senior Software Engineer",
            "description": "We are looking for a Senior Software Engineer with experience in Python, JavaScript, and React.",
            "requirements": "5+ years of experience, Bachelor's degree",
            "skills": "Python,JavaScript,React,Node.js,AWS",
            "experience_level": "Senior",
            "location": "Remote",
            "salary_range": "$100,000 - $150,000"
        }
        
        response = requests.post(f"{BACKEND_URL}/upload-job-description", data=job_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Job description uploaded successfully")
            print(f"   Job ID: {result['job_description']['id']}")
            return result['job_description']['id']
        else:
            print(f"❌ Job description upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing job description upload: {e}")
        return None

def test_resume_upload():
    """Test resume upload with a sample text file."""
    try:
        # Create a sample resume file
        sample_resume = """
        JOHN DOE
        Software Engineer
        john.doe@email.com
        +1-555-0123
        
        EXPERIENCE
        5 years of experience in software development
        
        SKILLS
        Python, JavaScript, React, Node.js, AWS, Docker
        
        EDUCATION
        Bachelor's Degree in Computer Science
        """
        
        # Create temporary file
        with open("sample_resume.txt", "w") as f:
            f.write(sample_resume)
        
        # Upload the file
        with open("sample_resume.txt", "rb") as f:
            files = {"file": ("sample_resume.txt", f, "text/plain")}
            response = requests.post(f"{BACKEND_URL}/upload-resume", files=files)
        
        # Clean up
        os.remove("sample_resume.txt")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Resume uploaded successfully")
            print(f"   Resume ID: {result['resume']['id']}")
            return result['resume']['id']
        else:
            print(f"❌ Resume upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing resume upload: {e}")
        return None

def test_matching(job_id, resume_id):
    """Test the matching functionality."""
    try:
        response = requests.post(f"{BACKEND_URL}/match", json={"job_description_id": job_id})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Matching completed successfully")
            print(f"   Total candidates: {result['total_candidates']}")
            print(f"   Matched candidates: {result['matched_candidates']}")
            
            if result['results']:
                top_match = result['results'][0]
                print(f"   Top match score: {top_match['similarity_score']:.2f}%")
                print(f"   Top candidate: {top_match['candidate_name']}")
                print(f"   Matched skills: {', '.join(top_match['matched_skills'])}")
            
            return True
        else:
            print(f"❌ Matching failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing matching: {e}")
        return False

def test_api_endpoints():
    """Test various API endpoints."""
    try:
        # Test getting resumes
        response = requests.get(f"{BACKEND_URL}/resumes")
        if response.status_code == 200:
            print("✅ GET /resumes endpoint working")
        else:
            print(f"❌ GET /resumes failed: {response.status_code}")
        
        # Test getting job descriptions
        response = requests.get(f"{BACKEND_URL}/job-descriptions")
        if response.status_code == 200:
            print("✅ GET /job-descriptions endpoint working")
        else:
            print(f"❌ GET /job-descriptions failed: {response.status_code}")
        
        # Test getting stats
        response = requests.get(f"{BACKEND_URL}/stats")
        if response.status_code == 200:
            result = response.json()
            print("✅ GET /stats endpoint working")
            print(f"   Total resumes: {result['stats']['total_resumes']}")
            print(f"   Total job descriptions: {result['stats']['total_job_descriptions']}")
        else:
            print(f"❌ GET /stats failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")

def main():
    """Run all tests."""
    print("🧠 AI-Powered Applicant Tracking System - Test Suite")
    print("=" * 60)
    
    # Test backend health
    if not test_backend_health():
        return
    
    print("\n📋 Testing Job Description Upload...")
    job_id = test_job_description_upload()
    
    print("\n📄 Testing Resume Upload...")
    resume_id = test_resume_upload()
    
    if job_id and resume_id:
        print("\n🔍 Testing Matching Functionality...")
        test_matching(job_id, resume_id)
    
    print("\n🔧 Testing API Endpoints...")
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("\nTo start using the system:")
    print("1. Backend: python backend.py")
    print("2. Frontend: cd frontend && npm run dev")
    print("3. Open: http://localhost:3000")

if __name__ == "__main__":
    main() 