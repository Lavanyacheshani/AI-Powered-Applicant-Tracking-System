import { createClient } from "@supabase/supabase-js"

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type Database = {
  public: {
    Tables: {
      job_descriptions: {
        Row: {
          id: string
          title: string
          description: string
          requirements: string | null
          skills: string[] | null
          experience_level: string | null
          location: string | null
          salary_range: string | null
          embedding: number[] | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          title: string
          description: string
          requirements?: string | null
          skills?: string[] | null
          experience_level?: string | null
          location?: string | null
          salary_range?: string | null
          embedding?: number[] | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          title?: string
          description?: string
          requirements?: string | null
          skills?: string[] | null
          experience_level?: string | null
          location?: string | null
          salary_range?: string | null
          embedding?: number[] | null
          created_at?: string
          updated_at?: string
        }
      }
      resumes: {
        Row: {
          id: string
          file_name: string
          candidate_name: string | null
          email: string | null
          phone: string | null
          experience_years: number | null
          skills: string[] | null
          education: string | null
          raw_text: string
          parsed_data: any | null
          embedding: number[] | null
          uploaded_at: string
        }
        Insert: {
          id?: string
          file_name: string
          candidate_name?: string | null
          email?: string | null
          phone?: string | null
          experience_years?: number | null
          skills?: string[] | null
          education?: string | null
          raw_text: string
          parsed_data?: any | null
          embedding?: number[] | null
          uploaded_at?: string
        }
        Update: {
          id?: string
          file_name?: string
          candidate_name?: string | null
          email?: string | null
          phone?: string | null
          experience_years?: number | null
          skills?: string[] | null
          education?: string | null
          raw_text?: string
          parsed_data?: any | null
          embedding?: number[] | null
          uploaded_at?: string
        }
      }
      match_results: {
        Row: {
          id: string
          job_description_id: string
          resume_id: string
          similarity_score: number
          matched_skills: string[] | null
          highlights: string[] | null
          is_shortlisted: boolean
          created_at: string
        }
        Insert: {
          id?: string
          job_description_id: string
          resume_id: string
          similarity_score: number
          matched_skills?: string[] | null
          highlights?: string[] | null
          is_shortlisted?: boolean
          created_at?: string
        }
        Update: {
          id?: string
          job_description_id?: string
          resume_id?: string
          similarity_score?: number
          matched_skills?: string[] | null
          highlights?: string[] | null
          is_shortlisted?: boolean
          created_at?: string
        }
      }
    }
  }
}
