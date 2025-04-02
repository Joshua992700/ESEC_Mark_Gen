"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import Image from "next/image"
import { ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'

export default function TeacherForm() {
  const [selectedClass, setSelectedClass] = useState("")
  const [excelFile, setExcelFile] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleClassChange = (value) => {
    setSelectedClass(value)
  }

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    setExcelFile(file)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setIsLoading(true)
    
    const formData = new FormData(event.target)

    try {
      const response = await fetch("http://127.0.0.1:5000/api/upload", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to upload file')
      }
      console.log("Successfully Uploaded")
      toast.success("File uploaded successfully!")
    } catch (error) {
      console.error("Error uploading file:", error)
      toast.error("The file is not uploaded. Please try re-uploading it.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <ToastContainer position="top-center" autoClose={5000} hideProgressBar={false} newestOnTop closeOnClick rtl={false} pauseOnFocusLoss draggable pauseOnHover />
      
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
          <div className="flex items-center">
            <Image
              src="https://erode-sengunthar.ac.in/wp-content/uploads/2023/02/ESEC_Logo.png"
              alt="College Logo"
              width={50}
              height={50}
              className="mr-3"
            />
            <h1 className="text-2xl font-bold text-gray-900">Erode Sengunthar Engineering College</h1>
          </div>
        </div>
      </header>

      <main className="flex-grow">
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <h2 className="text-center text-2xl font-semibold text-gray-900 mb-6">
            By Department of Artificial Intelligence and Data Science
          </h2>

          <Card className="max-w-md mx-auto">
            <CardHeader>
              <CardTitle>Teacher's Form</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-4" onSubmit={handleSubmit} encType="multipart/form-data">
                <div className="space-y-2">
                  <label htmlFor="class" className="text-sm font-medium text-gray-700">
                    Class
                  </label>
                  <Select onValueChange={handleClassChange}>
                    <SelectTrigger id="class">
                      <SelectValue placeholder="Select a class" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="class1">Class 1</SelectItem>
                      <SelectItem value="class2">Class 2</SelectItem>
                      <SelectItem value="class3">Class 3</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label htmlFor="excel-file" className="text-sm font-medium text-gray-700">
                    Upload your Excel File
                  </label>
                  <Input id="excel-file" name="excelFile" type="file" accept=".xlsx, .xls" required onChange={handleFileChange} />
                </div>
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? (
                    <div className="flex items-center justify-center">
                      <div className="loader"></div>
                      <span className="ml-2">Uploading...</span>
                    </div>
                  ) : (
                    "Submit"
                  )}
                </Button>
              </form>
            </CardContent>
            <CardFooter>
              <p className="text-sm text-gray-500">
                Excel Format Instructions: Please ensure your Excel file contains columns for Student Name, 
                Roll Number, and Marks. Each row should represent a single student's data.
              </p>
            </CardFooter>
          </Card>
        </div>
      </main>

      <footer className="bg-white shadow-sm mt-8">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 text-center text-gray-500">
          Developed by Joshua
        </div>
      </footer>

      <style jsx>{`
        .loader {
          width: 24px;
          height: 24px;
          border: 3px solid #ffffff;
          border-bottom-color: transparent;
          border-radius: 50%;
          display: inline-block;
          box-sizing: border-box;
          animation: rotation 1s linear infinite;
        }

        @keyframes rotation {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  )
}