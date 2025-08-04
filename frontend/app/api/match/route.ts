import { type NextRequest, NextResponse } from "next/server"
import { supabase } from "@/lib/supabase"
import { cosineSimilarity } from "ai"

export async function POST(request: NextRequest) {
  try {
    const { jobDescriptionId } = await request.json()

    // Get the job description with embedding
    const { data: jobDescription, error: jdError } = await supabase
      .from("job_descriptions")
      .select("*")
      .eq("id", jobDescriptionId)
      .single()

    if (jdError || !jobDescription) {
      return NextResponse.json({ error: "Job description not found" }, { status: 404 })
    }

    // Get all resumes with embeddings
    const { data: resumes, error: resumesError } = await supabase.from("resumes").select("*")

    if (resumesError) {
      return NextResponse.json({ error: resumesError.message }, { status: 500 })
    }

    // Use the Python backend for matching
    const backendResponse = await fetch("http://localhost:8000/match", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_description_id: jobDescriptionId,
      }),
    })

    if (!backendResponse.ok) {
      // Fallback to frontend matching if backend is not available
      console.warn("Backend not available, using frontend matching")
      
      // Calculate similarity scores using frontend
      const matchResults = resumes
        .map((resume) => {
          if (!jobDescription.embedding || !resume.embedding) {
            return null
          }

          const similarity = cosineSimilarity(jobDescription.embedding, resume.embedding)
          const score = Math.round(similarity * 100)

          // Find matched skills
          const jdSkills = jobDescription.skills || []
          const resumeSkills = resume.skills || []
          const matchedSkills = resumeSkills.filter((skill) =>
            jdSkills.some(
              (jdSkill) =>
                jdSkill.toLowerCase().includes(skill.toLowerCase()) ||
                skill.toLowerCase().includes(jdSkill.toLowerCase()),
            ),
          )

          const highlights = [
            `${resume.experience_years || 0} years of experience`,
            `${matchedSkills.length} matching skills`,
            resume.education || "Education not specified",
          ]

          return {
            resume,
            similarity_score: score,
            matched_skills: matchedSkills,
            highlights,
          }
        })
        .filter(Boolean)
        .sort((a, b) => b!.similarity_score - a!.similarity_score)

      // Store match results in database
      const matchInserts = matchResults.map((result) => ({
        job_description_id: jobDescriptionId,
        resume_id: result!.resume.id,
        similarity_score: result!.similarity_score / 100, // Store as decimal
        matched_skills: result!.matched_skills,
        highlights: result!.highlights,
      }))

      // Delete existing matches for this job description
      await supabase.from("match_results").delete().eq("job_description_id", jobDescriptionId)

      // Insert new matches
      const { error: insertError } = await supabase.from("match_results").insert(matchInserts)

      if (insertError) {
        console.error("Error storing match results:", insertError)
      }

      return NextResponse.json(matchResults)
    }

    // Use backend results
    const backendData = await backendResponse.json()
    
    if (!backendData.success) {
      return NextResponse.json({ error: backendData.message || "Matching failed" }, { status: 500 })
    }

    // Store backend results in database
    const matchInserts = backendData.results.map((result: any) => ({
      job_description_id: jobDescriptionId,
      resume_id: result.resume_id,
      similarity_score: result.similarity_score / 100, // Store as decimal
      matched_skills: result.matched_skills,
      highlights: result.highlights,
    }))

    // Delete existing matches for this job description
    await supabase.from("match_results").delete().eq("job_description_id", jobDescriptionId)

    // Insert new matches
    const { error: insertError } = await supabase.from("match_results").insert(matchInserts)

    if (insertError) {
      console.error("Error storing match results:", insertError)
    }

    // Format results for frontend
    const formattedResults = backendData.results.map((result: any) => ({
      resume: {
        id: result.resume_id,
        candidate_name: result.candidate_name,
        email: result.email,
        file_name: result.file_name,
        experience_years: result.experience_years,
        skills: result.skills,
        education: result.education,
      },
      similarity_score: result.similarity_score,
      matched_skills: result.matched_skills,
      highlights: result.highlights,
    }))

    return NextResponse.json(formattedResults)
  } catch (error) {
    console.error("Error performing matching:", error)
    return NextResponse.json({ error: "Failed to perform matching" }, { status: 500 })
  }
}
