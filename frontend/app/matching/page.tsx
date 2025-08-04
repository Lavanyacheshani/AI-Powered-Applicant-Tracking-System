"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ArrowLeft, Search, Download, Star } from "lucide-react"
import Link from "next/link"

interface JobDescription {
  id: string
  title: string
  description: string
  createdAt: string
}

interface Resume {
  id: string
  fileName: string
  name: string
  email: string
  experience: number
  skills: string[]
  education: string
  uploadedAt: string
}

interface MatchResult {
  resume: Resume
  score: number
  matchedSkills: string[]
  highlights: string[]
}

export default function MatchingPage() {
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([])
  const [resumes, setResumes] = useState<Resume[]>([])
  const [selectedJD, setSelectedJD] = useState<string>("")
  const [matchResults, setMatchResults] = useState<MatchResult[]>([])
  const [isMatching, setIsMatching] = useState(false)
  const [shortlisted, setShortlisted] = useState<Set<string>>(new Set())

  useEffect(() => {
    // Load job descriptions from Python backend
    const fetchJobDescriptions = async () => {
      try {
        const response = await fetch("http://localhost:8000/job-descriptions")
        const data = await response.json()
        if (data.success) {
          setJobDescriptions(data.job_descriptions)
        }
      } catch (error) {
        console.error("Error fetching job descriptions:", error)
      }
    }

    fetchJobDescriptions()
  }, [])

  const performMatching = async () => {
    if (!selectedJD) return

    setIsMatching(true)

    try {
      const response = await fetch("http://localhost:8000/match", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          job_description_id: parseInt(selectedJD),
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to perform matching")
      }

      const data = await response.json()
      if (data.success) {
        setMatchResults(
          data.results.map((result: any) => ({
            resume: {
              id: result.resume_id,
              fileName: result.file_name,
              name: result.candidate_name,
              email: result.email,
              experience: result.experience_years,
              skills: result.skills,
              education: result.education,
              uploadedAt: new Date().toISOString(),
            },
            score: result.similarity_score,
            matchedSkills: result.matched_skills,
            highlights: result.highlights,
          })),
        )
      }
    } catch (error) {
      console.error("Error performing matching:", error)
      alert("Failed to perform matching. Please try again.")
    } finally {
      setIsMatching(false)
    }
  }

  const toggleShortlist = (resumeId: string) => {
    const newShortlisted = new Set(shortlisted)
    if (newShortlisted.has(resumeId)) {
      newShortlisted.delete(resumeId)
    } else {
      newShortlisted.add(resumeId)
    }
    setShortlisted(newShortlisted)
  }

  const exportResults = () => {
    const csvContent = [
      ["Name", "Email", "Score", "Experience", "Skills", "Shortlisted"].join(","),
      ...matchResults.map((result) =>
        [
          result.resume.name,
          result.resume.email,
          result.score,
          result.resume.experience,
          result.resume.skills.join(";"),
          shortlisted.has(result.resume.id) ? "Yes" : "No",
        ].join(","),
      ),
    ].join("\n")

    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "matching-results.csv"
    a.click()
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return "bg-green-100"
    if (score >= 60) return "bg-yellow-100"
    return "bg-red-100"
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-800">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Match Candidates</h1>
          <p className="text-gray-600">Select a job description to find the best matching candidates</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Job Selection</CardTitle>
                <CardDescription>Choose a job description to match against</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Select value={selectedJD} onValueChange={setSelectedJD}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a job description" />
                    </SelectTrigger>
                    <SelectContent>
                      {jobDescriptions.map((jd) => (
                        <SelectItem key={jd.id} value={jd.id}>
                          {jd.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <Button onClick={performMatching} className="w-full" disabled={!selectedJD || isMatching}>
                  {isMatching ? (
                    <>
                      <Search className="h-4 w-4 mr-2 animate-spin" />
                      Matching...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Match Candidates
                    </>
                  )}
                </Button>

                {matchResults.length > 0 && (
                  <div className="pt-4 border-t">
                    <div className="text-sm text-gray-600 mb-2">Found {matchResults.length} candidates</div>
                    <div className="text-sm text-gray-600 mb-4">Shortlisted: {shortlisted.size}</div>
                    <Button onClick={exportResults} variant="outline" className="w-full bg-transparent">
                      <Download className="h-4 w-4 mr-2" />
                      Export Results
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2">
            {matchResults.length > 0 ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold">Matching Results</h2>
                  <Badge variant="secondary">{matchResults.length} candidates found</Badge>
                </div>

                {matchResults.map((result, index) => (
                  <Card key={result.resume.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-semibold">{result.resume.name}</h3>
                            <Badge variant="outline">#{index + 1}</Badge>
                            {shortlisted.has(result.resume.id) && (
                              <Star className="h-4 w-4 text-yellow-500 fill-current" />
                            )}
                          </div>
                          <p className="text-gray-600">{result.resume.email}</p>
                        </div>
                        <div className="text-right">
                          <div className={`text-2xl font-bold ${getScoreColor(result.score)}`}>{result.score}%</div>
                          <div className="text-sm text-gray-500">Match Score</div>
                        </div>
                      </div>

                      <div className="mb-4">
                        <Progress value={result.score} className={`h-2 ${getScoreBgColor(result.score)}`} />
                      </div>

                      <div className="grid md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <h4 className="font-medium mb-2">Matched Skills</h4>
                          <div className="flex flex-wrap gap-1">
                            {result.matchedSkills.map((skill) => (
                              <Badge key={skill} variant="secondary" className="text-xs">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">Highlights</h4>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {result.highlights.map((highlight, idx) => (
                              <li key={idx}>• {highlight}</li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      <div className="flex justify-between items-center">
                        <div className="text-sm text-gray-500">File: {result.resume.fileName}</div>
                        <Button
                          variant={shortlisted.has(result.resume.id) ? "default" : "outline"}
                          size="sm"
                          onClick={() => toggleShortlist(result.resume.id)}
                        >
                          <Star className="h-4 w-4 mr-1" />
                          {shortlisted.has(result.resume.id) ? "Shortlisted" : "Shortlist"}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Yet</h3>
                  <p className="text-gray-600">Select a job description and click "Match Candidates" to see results</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
