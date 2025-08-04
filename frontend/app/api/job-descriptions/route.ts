import { type NextRequest, NextResponse } from "next/server"
import { supabase } from "@/lib/supabase"
import { embed } from "ai"
import { openai } from "@ai-sdk/openai"

export async function GET() {
  try {
    const { data, error } = await supabase
      .from("job_descriptions")
      .select("*")
      .order("created_at", { ascending: false })

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch job descriptions" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { title, description, requirements, skills, experience_level, location, salary_range } = body

    // Generate embedding for the job description
    const { embedding } = await embed({
      model: openai.embedding("text-embedding-3-small"),
      value: `${title} ${description} ${requirements || ""} ${skills?.join(" ") || ""}`,
    })

    const { data, error } = await supabase
      .from("job_descriptions")
      .insert({
        title,
        description,
        requirements,
        skills,
        experience_level,
        location,
        salary_range,
        embedding,
      })
      .select()
      .single()

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Error creating job description:", error)
    return NextResponse.json({ error: "Failed to create job description" }, { status: 500 })
  }
}
