import { type NextRequest, NextResponse } from "next/server"
import { supabase } from "@/lib/supabase"
import { embed } from "ai"
import { openai } from "@ai-sdk/openai"

export async function GET() {
  try {
    const { data, error } = await supabase.from("resumes").select("*").order("uploaded_at", { ascending: false })

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch resumes" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const files = formData.getAll("files") as File[]

    const results = []

    for (const file of files) {
      // Create a new FormData for each file to send to backend
      const backendFormData = new FormData()
      backendFormData.append("file", file)

      // Send to Python backend for processing
      const backendResponse = await fetch("http://localhost:8000/upload-resume", {
        method: "POST",
        body: backendFormData,
      })

      if (!backendResponse.ok) {
        console.error(`Error processing ${file.name}:`, await backendResponse.text())
        continue
      }

      const backendData = await backendResponse.json()
      const resumeData = backendData.resume

      // Generate embedding for the resume using OpenAI
      const { embedding } = await embed({
        model: openai.embedding("text-embedding-3-small"),
        value: `${resumeData.candidate_name} ${resumeData.raw_text} ${resumeData.skills.join(" ")} ${resumeData.education}`,
      })

      // Store in Supabase
      const { data, error } = await supabase
        .from("resumes")
        .insert({
          file_name: resumeData.file_name,
          candidate_name: resumeData.candidate_name,
          email: resumeData.email,
          phone: resumeData.phone,
          experience_years: resumeData.experience_years,
          skills: resumeData.skills,
          education: resumeData.education,
          raw_text: resumeData.raw_text,
          embedding,
          parsed_data: {
            candidate_name: resumeData.candidate_name,
            email: resumeData.email,
            phone: resumeData.phone,
            experience_years: resumeData.experience_years,
            skills: resumeData.skills,
            education: resumeData.education,
          },
        })
        .select()
        .single()

      if (error) {
        console.error("Error inserting resume:", error)
        continue
      }

      results.push(data)
    }

    return NextResponse.json(results)
  } catch (error) {
    console.error("Error processing resumes:", error)
    return NextResponse.json({ error: "Failed to process resumes" }, { status: 500 })
  }
}
