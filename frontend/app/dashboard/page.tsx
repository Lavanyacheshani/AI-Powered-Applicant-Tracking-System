"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowLeft, FileText, Users, Trash2, Eye } from "lucide-react"
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

export default function DashboardPage() {
  const [jobDescriptions, setJobDescriptions] = useState<JobDescription[]>([])
  const [resumes, setResumes] = useState<Resume[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch job descriptions from Python backend
        const jdResponse = await fetch("http://localhost:8000/job-descriptions")
        const jdData = await jdResponse.json()
        if (jdData.success) {
          setJobDescriptions(jdData.job_descriptions)
        }

        // Fetch resumes from Python backend
        const resumeResponse = await fetch("http://localhost:8000/resumes")
        const resumeData = await resumeResponse.json()
        if (resumeData.success) {
          setResumes(resumeData.resumes)
        }
      } catch (error) {
        console.error("Error fetching data:", error)
      }
    }

    fetchData()
  }, [])

  const deleteJD = (id: string) => {
    const updated = jobDescriptions.filter((jd) => jd.id !== id)
    setJobDescriptions(updated)
    localStorage.setItem("jobDescriptions", JSON.stringify(updated))
  }

  const deleteResume = (id: string) => {
    const updated = resumes.filter((resume) => resume.id !== id)
    setResumes(updated)
    localStorage.setItem("resumes", JSON.stringify(updated))
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
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
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
          <p className="text-gray-600">Manage your job descriptions and candidate resumes</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Job Descriptions</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{jobDescriptions.length}</div>
              <p className="text-xs text-muted-foreground">Active job postings</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Resumes</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{resumes.length}</div>
              <p className="text-xs text-muted-foreground">Candidate profiles</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Match Rate</CardTitle>
              <Badge variant="secondary">Demo</Badge>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">78%</div>
              <p className="text-xs text-muted-foreground">Average compatibility</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="job-descriptions" className="space-y-4">
          <TabsList>
            <TabsTrigger value="job-descriptions">Job Descriptions</TabsTrigger>
            <TabsTrigger value="resumes">Resumes</TabsTrigger>
          </TabsList>

          <TabsContent value="job-descriptions" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Job Descriptions</h2>
              <Link href="/upload-jd">
                <Button>Add New JD</Button>
              </Link>
            </div>

            {jobDescriptions.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Job Descriptions</h3>
                  <p className="text-gray-600 mb-4">Upload your first job description to get started</p>
                  <Link href="/upload-jd">
                    <Button>Upload Job Description</Button>
                  </Link>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {jobDescriptions.map((jd) => (
                  <Card key={jd.id}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle>{jd.title}</CardTitle>
                          <CardDescription>Created on {formatDate(jd.createdAt)}</CardDescription>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => deleteJD(jd.id)}>
                            <Trash2 className="h-4 w-4 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600 line-clamp-3">{jd.description.substring(0, 200)}...</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="resumes" className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Candidate Resumes</h2>
              <Link href="/upload-resumes">
                <Button>Upload Resumes</Button>
              </Link>
            </div>

            {resumes.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Resumes</h3>
                  <p className="text-gray-600 mb-4">Upload candidate resumes to start matching</p>
                  <Link href="/upload-resumes">
                    <Button>Upload Resumes</Button>
                  </Link>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {resumes.map((resume) => (
                  <Card key={resume.id}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle>{resume.name}</CardTitle>
                          <CardDescription>{resume.email}</CardDescription>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => deleteResume(resume.id)}>
                            <Trash2 className="h-4 w-4 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid md:grid-cols-3 gap-4">
                        <div>
                          <div className="text-sm font-medium">Experience</div>
                          <div className="text-sm text-gray-600">{resume.experience} years</div>
                        </div>
                        <div>
                          <div className="text-sm font-medium">Education</div>
                          <div className="text-sm text-gray-600">{resume.education}</div>
                        </div>
                        <div>
                          <div className="text-sm font-medium">File</div>
                          <div className="text-sm text-gray-600">{resume.fileName}</div>
                        </div>
                      </div>
                      <div className="mt-4">
                        <div className="text-sm font-medium mb-2">Skills</div>
                        <div className="flex flex-wrap gap-1">
                          {resume.skills.map((skill) => (
                            <Badge key={skill} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
