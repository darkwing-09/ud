import { useState } from 'react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { UserAvatar } from '@/components/ui/avatar'
import { Award, Save, Info, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'

export default function MarksEntryPage() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [examId, setExamId] = useState('exam-mid-term')
  
  // Mock students
  const [marks, setMarks] = useState<Record<string, { theory: string, practical: string }>>({
    'stu-1': { theory: '85', practical: '18' },
    'stu-2': { theory: '90', practical: '20' },
    'stu-3': { theory: '72', practical: '15' },
    'stu-4': { theory: '', practical: '' },
    'stu-5': { theory: '', practical: '' },
  })

  // 1 = Aarav, 2 = Aditi, etc
  const students = [
    { id: 'stu-1', name: 'Aarav Sharma', roll: '01' },
    { id: 'stu-2', name: 'Aditi Verma', roll: '02' },
    { id: 'stu-3', name: 'Aryan Gupta', roll: '03' },
    { id: 'stu-4', name: 'Diya Patel', roll: '04' },
    { id: 'stu-5', name: 'Ishaan Singh', roll: '05' },
  ]

  const handleChange = (id: string, type: 'theory' | 'practical', val: string) => {
    setMarks(prev => ({
      ...prev,
      [id]: { ...prev[id], [type]: val }
    }))
  }

  const handleSave = () => {
    setIsSubmitting(true)
    setTimeout(() => {
      toast.success('Marks saved securely.')
      setIsSubmitting(false)
    }, 1500)
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl mx-auto">
      <PageHeader
        title="Enter Marks"
        description="Select an examination and record student marks."
      />

      <div className="grid gap-6 md:grid-cols-4">
        {/* Sidebar Configuration */}
        <div className="md:col-span-1 space-y-6">
          <Card>
            <CardHeader className="pb-3 border-b border-border">
              <CardTitle className="text-sm font-semibold">Exam Configuration</CardTitle>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-muted-foreground uppercase">Select Exam</label>
                <select 
                  className="flex h-9 w-full rounded-md border border-input bg-input px-3 py-1 text-sm focus:ring-2 focus:ring-ring text-foreground"
                  value={examId}
                  onChange={e => setExamId(e.target.value)}
                >
                  <option value="exam-mid-term">Mid Term (Oct 2026)</option>
                  <option value="exam-periodic-1">Periodic Test 1</option>
                  <option value="exam-final">Final Exam</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-muted-foreground uppercase">Class & Section</label>
                <select className="flex h-9 w-full rounded-md border border-input bg-input px-3 py-1 text-sm focus:ring-2 focus:ring-ring text-foreground">
                  <option>Class 10 - A</option>
                  <option>Class 9 - B</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-muted-foreground uppercase">Subject</label>
                <select className="flex h-9 w-full rounded-md border border-input bg-input px-3 py-1 text-sm focus:ring-2 focus:ring-ring text-foreground">
                  <option>Mathematics</option>
                  <option>Science</option>
                </select>
              </div>

              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 mt-4 text-xs">
                <p className="font-semibold text-blue-500 flex items-center gap-1.5 mb-1.5"><Info className="size-3.5"/> Guidelines</p>
                <ul className="text-muted-foreground space-y-1 pl-5 list-disc">
                  <li>Theory max: 80</li>
                  <li>Practical max: 20</li>
                  <li>Leave blank for students who were absent.</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* SpreadSheet Area */}
        <div className="md:col-span-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-border bg-muted/10">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Award className="size-4 text-primary" /> Grade Sheet Entry
              </CardTitle>
              <Button size="sm" onClick={handleSave} loading={isSubmitting} className="shadow-lg shadow-primary/20">
                <Save className="mr-2 size-4" /> Save Marks
              </Button>
            </CardHeader>
            <CardContent className="p-0 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/30">
                    <th className="px-4 py-3 text-left font-semibold text-muted-foreground uppercase tracking-wider text-xs">Student</th>
                    <th className="px-4 py-3 text-left font-semibold text-muted-foreground uppercase tracking-wider text-xs">Theory (80)</th>
                    <th className="px-4 py-3 text-left font-semibold text-muted-foreground uppercase tracking-wider text-xs">Practical (20)</th>
                    <th className="px-4 py-3 text-left font-semibold text-muted-foreground uppercase tracking-wider text-xs">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {students.map((student) => {
                    const t = parseInt(marks[student.id]?.theory || '0', 10) || 0
                    const p = parseInt(marks[student.id]?.practical || '0', 10) || 0
                    const total = t + p
                    const isError = t > 80 || p > 20

                    return (
                      <tr key={student.id} className={`hover:bg-muted/10 transition-colors ${isError ? 'bg-rose-500/5' : ''}`}>
                        <td className="px-4 py-3 min-w-[200px]">
                          <div className="flex items-center gap-3">
                            <span className="w-6 text-xs text-muted-foreground font-mono">{student.roll}</span>
                            <UserAvatar name={student.name} size="sm" className="hidden sm:flex" />
                            <span className="font-medium text-foreground">{student.name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-2">
                          <Input 
                            type="number" 
                            min="0" max="80"
                            className={`w-24 h-9 text-center ${t > 80 ? 'border-rose-500' : ''}`}
                            value={marks[student.id]?.theory}
                            onChange={(e) => handleChange(student.id, 'theory', e.target.value)}
                          />
                        </td>
                        <td className="px-4 py-2">
                          <Input 
                            type="number" 
                            min="0" max="20"
                            className={`w-24 h-9 text-center ${p > 20 ? 'border-rose-500' : ''}`}
                            value={marks[student.id]?.practical}
                            onChange={(e) => handleChange(student.id, 'practical', e.target.value)}
                          />
                        </td>
                        <td className="px-4 py-3 font-semibold font-mono text-primary">
                          {marks[student.id]?.theory === '' && marks[student.id]?.practical === '' ? '--' : total}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
              <div className="p-4 bg-muted/10 border-t border-border flex items-center gap-3 text-xs text-muted-foreground">
                <AlertCircle className="size-4" /> Ensure all values fall within their respective maximum parameters before saving.
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
