# 🧠 AI-Powered Applicant Tracking System (CV + JD Matching)

An intelligent, NLP-driven Applicant Tracking System that automates the process of matching **resumes (CVs)** to **job descriptions (JDs)**. It helps recruiters identify the **best-fit candidates** efficiently using machine learning techniques.

## 🔍 Key Features

- ✅ **Upload Job Descriptions and multiple Resumes**
- ✅ **Automatically extract and process textual content** from PDF, DOCX, and TXT files
- ✅ **Match resumes to job descriptions using:**
  - TF-IDF + Cosine Similarity (fast and interpretable)
  - BERT embeddings (for deeper semantic understanding)
- ✅ **Rank candidates based on similarity score**
- ✅ **Highlight matched keywords and phrases**
- ✅ **User-friendly web portal** for HR/admin use
- ✅ **Real-time processing** with FastAPI backend
- ✅ **Modern React/Next.js frontend** with beautiful UI

## 📊 Model Options

| Model Type                   | Description                                   | Libraries                               | Performance                     |
| ---------------------------- | --------------------------------------------- | --------------------------------------- | ------------------------------- |
| TF-IDF + Cosine Similarity   | Lightweight, interpretable, suitable for MVPs | `scikit-learn`, `nltk`                  | Fast, good for keyword matching |
| BERT / Sentence-BERT (sBERT) | Context-aware, better accuracy                | `transformers`, `sentence-transformers` | Slower but more accurate        |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Supabase account (for database)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Powered-Applicant-Tracking-System
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI backend
python backend.py
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Set up environment variables
cp .env.example .env.local
```

Edit `.env.local` with your Supabase credentials:

```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
```

### 4. Database Setup

Run the SQL script in your Supabase dashboard:

```sql
-- Create job_descriptions table
CREATE TABLE IF NOT EXISTS job_descriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  requirements TEXT,
  skills TEXT[],
  experience_level TEXT,
  location TEXT,
  salary_range TEXT,
  embedding VECTOR(1536), -- For OpenAI embeddings
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create resumes table
CREATE TABLE IF NOT EXISTS resumes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  file_name TEXT NOT NULL,
  candidate_name TEXT,
  email TEXT,
  phone TEXT,
  experience_years INTEGER,
  skills TEXT[],
  education TEXT,
  raw_text TEXT NOT NULL,
  parsed_data JSONB,
  embedding VECTOR(1536), -- For OpenAI embeddings
  uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create match_results table to store matching results
CREATE TABLE IF NOT EXISTS match_results (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  job_description_id UUID REFERENCES job_descriptions(id) ON DELETE CASCADE,
  resume_id UUID REFERENCES resumes(id) ON DELETE CASCADE,
  similarity_score FLOAT NOT NULL,
  matched_skills TEXT[],
  highlights TEXT[],
  is_shortlisted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(job_description_id, resume_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_job_descriptions_embedding ON job_descriptions USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_resumes_embedding ON resumes USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_match_results_job_id ON match_results(job_description_id);
CREATE INDEX IF NOT EXISTS idx_match_results_resume_id ON match_results(resume_id);
CREATE INDEX IF NOT EXISTS idx_match_results_score ON match_results(similarity_score DESC);
```

### 5. Start the Application

```bash
# Start the frontend (in frontend directory)
npm run dev
# or
pnpm dev
```

The application will be available at `http://localhost:3000`

## 📁 Project Structure

```
AI-Powered-Applicant-Tracking-System/
├── backend.py                 # FastAPI backend server
├── resumematcher.py          # Core AI matching logic
├── requirements.txt          # Python dependencies
├── frontend/                 # Next.js frontend
│   ├── app/                  # Next.js app directory
│   │   ├── api/             # API routes
│   │   ├── dashboard/       # Dashboard page
│   │   ├── matching/        # Matching page
│   │   ├── upload-jd/       # Job description upload
│   │   └── upload-resumes/  # Resume upload
│   ├── components/          # React components
│   ├── lib/                 # Utilities and configurations
│   └── scripts/             # Database scripts
├── model/                   # ML models and datasets
└── README.md               # This file
```

## 🎯 Usage Guide

### 1. Upload Job Description

1. Navigate to "Upload JD" from the home page
2. Enter job title and description
3. Optionally upload a job description file (PDF, DOCX, TXT)
4. Click "Upload Job Description"

### 2. Upload Resumes

1. Navigate to "Upload Resumes" from the home page
2. Select multiple resume files (PDF, DOCX)
3. Click "Upload Resumes"
4. The system will automatically:
   - Extract text from files
   - Parse candidate information
   - Generate embeddings
   - Store in database

### 3. Match Candidates

1. Navigate to "Match & Rank" from the home page
2. Select a job description from the dropdown
3. Click "Match Candidates"
4. View ranked results with:
   - Similarity scores
   - Matched skills
   - Candidate highlights
   - Shortlist options

### 4. Dashboard

1. Navigate to "Dashboard" to view:
   - All job descriptions
   - All uploaded resumes
   - System statistics
   - Manage uploads

## 🔧 API Endpoints

### Backend (FastAPI - Port 8000)

- `GET /` - Health check
- `POST /upload-resume` - Upload and process resume
- `POST /upload-job-description` - Upload job description
- `GET /resumes` - Get all resumes
- `GET /job-descriptions` - Get all job descriptions
- `POST /match` - Match resumes to job description
- `POST /match-all` - Match all resumes to all job descriptions
- `DELETE /resume/{id}` - Delete resume
- `DELETE /job-description/{id}` - Delete job description
- `GET /stats` - Get system statistics

### Frontend (Next.js - Port 3000)

- `GET /api/job-descriptions` - Get job descriptions from Supabase
- `POST /api/job-descriptions` - Create job description
- `GET /api/resumes` - Get resumes from Supabase
- `POST /api/resumes` - Upload resumes
- `POST /api/match` - Perform matching

## 🧠 AI Models

### TF-IDF + Cosine Similarity

- **Pros**: Fast, interpretable, lightweight
- **Cons**: Limited semantic understanding
- **Use case**: Quick MVP, keyword-based matching

### BERT Embeddings

- **Pros**: Better semantic understanding, context-aware
- **Cons**: Slower, requires more resources
- **Use case**: Production systems, complex matching

## 📊 Supported File Formats

- **PDF**: Using PyPDF2
- **DOCX**: Using python-docx
- **TXT**: Plain text files

## 🔍 Text Processing Features

- **Text Extraction**: From PDF, DOCX, and TXT files
- **Text Cleaning**: Remove URLs, numbers, special characters
- **Information Extraction**:
  - Candidate name
  - Email addresses
  - Phone numbers
  - Experience years
  - Skills (programming languages, frameworks, tools)
  - Education level
- **Embedding Generation**: Using OpenAI's text-embedding-3-small

## 🎨 UI Features

- **Modern Design**: Built with Tailwind CSS and shadcn/ui
- **Responsive**: Works on desktop and mobile
- **Real-time Updates**: Live data from backend
- **File Upload**: Drag-and-drop support
- **Progress Indicators**: Loading states for all operations
- **Export Functionality**: Download results as CSV
- **Shortlisting**: Mark candidates as shortlisted

## 🚀 Deployment

### Backend Deployment

```bash
# Using uvicorn
uvicorn backend:app --host 0.0.0.0 --port 8000

# Using Docker
docker build -t ats-backend .
docker run -p 8000:8000 ats-backend
```

### Frontend Deployment

```bash
# Build for production
npm run build

# Start production server
npm start

# Deploy to Vercel
vercel --prod
```

## 🔧 Configuration

### Environment Variables

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Backend
BACKEND_URL=http://localhost:8000
```

### Model Configuration

In `resumematcher.py`, you can configure:

```python
# Choose model type
matcher = ResumeMatcher(model_type="bert")  # or "tfidf"

# Configure TF-IDF parameters
self.tfidf_vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words='english',
    ngram_range=(1, 2)
)

# Configure BERT model
self.bert_model = SentenceTransformer('all-MiniLM-L6-v2')
```

## 📈 Performance Optimization

1. **Vector Indexing**: Use Supabase's vector similarity search
2. **Caching**: Cache embeddings and results
3. **Batch Processing**: Process multiple files in batches
4. **Model Optimization**: Use quantized models for production

## 🔒 Security Considerations

- **File Validation**: Check file types and sizes
- **Input Sanitization**: Clean user inputs
- **Rate Limiting**: Prevent abuse
- **Authentication**: Add user authentication (not included)
- **Data Privacy**: Handle sensitive candidate data carefully

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) for BERT embeddings
- [scikit-learn](https://scikit-learn.org/) for TF-IDF implementation
- [Next.js](https://nextjs.org/) for the frontend framework
- [Supabase](https://supabase.com/) for the database
- [shadcn/ui](https://ui.shadcn.com/) for the UI components

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Happy Recruiting! 🎉**
