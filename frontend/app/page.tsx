import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileText, Users, BarChart3 } from "lucide-react"
import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">AI-Powered Resume Matcher</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Streamline your recruitment process with intelligent job description and resume matching
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="text-center">
              <FileText className="h-12 w-12 text-blue-600 mx-auto mb-2" />
              <CardTitle>Upload JD</CardTitle>
              <CardDescription>Upload and manage job descriptions</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/upload-jd">
                <Button className="w-full">Get Started</Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="text-center">
              <Upload className="h-12 w-12 text-green-600 mx-auto mb-2" />
              <CardTitle>Upload Resumes</CardTitle>
              <CardDescription>Bulk upload candidate resumes</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/upload-resumes">
                <Button className="w-full bg-transparent" variant="outline">
                  Upload Files
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="text-center">
              <BarChart3 className="h-12 w-12 text-purple-600 mx-auto mb-2" />
              <CardTitle>Match & Rank</CardTitle>
              <CardDescription>AI-powered candidate matching</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/matching">
                <Button className="w-full bg-transparent" variant="outline">
                  View Matches
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="text-center">
              <Users className="h-12 w-12 text-orange-600 mx-auto mb-2" />
              <CardTitle>Dashboard</CardTitle>
              <CardDescription>View all candidates and results</CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/dashboard">
                <Button className="w-full bg-transparent" variant="outline">
                  Open Dashboard
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="font-semibold mb-2">Upload Job Description</h3>
              <p className="text-gray-600 text-sm">Submit your job requirements and specifications</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600">2</span>
              </div>
              <h3 className="font-semibold mb-2">Upload Resumes</h3>
              <p className="text-gray-600 text-sm">Bulk upload candidate resumes in PDF or DOCX format</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600">3</span>
              </div>
              <h3 className="font-semibold mb-2">AI Matching</h3>
              <p className="text-gray-600 text-sm">Our AI analyzes and scores candidate compatibility</p>
            </div>
            <div className="text-center">
              <div className="bg-orange-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-orange-600">4</span>
              </div>
              <h3 className="font-semibold mb-2">Review Results</h3>
              <p className="text-gray-600 text-sm">View ranked candidates and export shortlists</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
