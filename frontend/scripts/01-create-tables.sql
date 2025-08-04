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

-- Enable Row Level Security
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_results ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your auth requirements)
CREATE POLICY "Allow all operations for authenticated users" ON job_descriptions
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON resumes
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all operations for authenticated users" ON match_results
  FOR ALL USING (auth.role() = 'authenticated');
