import { useState } from 'react'
import { PageHeader } from '@/components/common/PageHeader'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {} from '@/components/ui/avatar'
import { Search, Wallet, CheckCircle2, AlertCircle, Receipt, CreditCard, Banknote } from 'lucide-react'
import { formatCurrency, formatDate } from '@/lib/utils'
import { toast } from 'sonner'

type FeeItem = {
  id: string
  name: string
  amount: number
  due_date: string
  status: 'PAID' | 'PARTIAL' | 'PENDING'
  paid_amount: number
}

// Mock Search Result
const SEARCH_RESULT = {
  student: {
    id: 'STU-2023-089',
    name: 'Aarav Sharma',
    class: 'Class 10',
    section: 'A',
    roll_no: '12',
    avatar_url: null,
  },
  fees: [
    { id: 'f1', name: 'Tuition Fee (Oct-Dec)', amount: 15000, due_date: '2026-10-15', status: 'PENDING', paid_amount: 0 },
    { id: 'f2', name: 'Transport Fee (Oct)', amount: 2500, due_date: '2026-10-15', status: 'PENDING', paid_amount: 0 },
    { id: 'f3', name: 'Lab and Library Fee', amount: 3000, due_date: '2026-09-15', status: 'PAID', paid_amount: 3000 },
  ] as FeeItem[]
}

export default function FeeCollectPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [result, setResult] = useState<typeof SEARCH_RESULT | null>(null)
  
  const [selectedFees, setSelectedFees] = useState<Set<string>>(new Set())
  const [isProcessing, setIsProcessing] = useState(false)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchTerm.trim()) return
    setIsSearching(true)
    setTimeout(() => {
      setResult(SEARCH_RESULT)
      setSelectedFees(new Set(['f1', 'f2'])) // auto-select pending
      setIsSearching(false)
    }, 800)
  }

  const toggleFee = (id: string) => {
    const next = new Set(selectedFees)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    setSelectedFees(next)
  }

  const handleCollect = () => {
    if (selectedFees.size === 0) return toast.error('Please select at least one fee item')
    setIsProcessing(true)
    setTimeout(() => {
      toast.success('Fee collected successfully. Receipt generated.')
      // reset
      setResult(null)
      setSelectedFees(new Set())
      setSearchTerm('')
      setIsProcessing(false)
    }, 1500)
  }

  const totalToPay = result?.fees
    .filter(f => selectedFees.has(f.id))
    .reduce((acc, f) => acc + (f.amount - f.paid_amount), 0) ?? 0

  return (
    <div className="space-y-6 animate-fade-in max-w-5xl mx-auto">
      <PageHeader
        title="Collect Fees"
        description="Search for a student and record fee payments"
        breadcrumbs={[
          { label: 'Admin' },
          { label: 'Fees', href: '/admin/fees' },
          { label: 'Collect' }
        ]}
      />

      {/* Search Bar */}
      <Card>
        <CardContent className="p-4 sm:p-6">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground ml-1">Search Student</label>
              <Input 
                placeholder="Enter Student Name, Admission No. or Roll No..." 
                leftIcon={<Search />}
                className="h-11 shadow-sm"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button type="submit" loading={isSearching} className="h-11 px-8 shadow-primary/20 shadow-md w-full sm:w-auto">
                Discover
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Result Panel */}
      {result && (
        <div className="grid gap-6 lg:grid-cols-3 animate-slide-up-fade">
          
          {/* Left: Student Profile */}
          <div className="lg:col-span-1 space-y-6">
            <Card className="overflow-hidden">
              <div className="h-16 bg-gradient-to-r from-blue-600/40 to-primary/40" />
              <CardContent className="p-6 pt-0 text-center relative">
                <UserAvatar 
                  name={result.student.name} 
                  src={result.student.avatar_url} 
                  size="xl" 
                  className="mx-auto -mt-10 mb-3 ring-4 ring-background border border-border"
                />
                <h3 className="text-xl font-bold text-foreground">{result.student.name}</h3>
                <p className="text-sm text-primary font-medium mt-1">
                  {result.student.class} - {result.student.section}
                </p>
                <div className="bg-muted/30 rounded-lg p-3 mt-4 text-xs flex justify-between">
                  <div className="text-center">
                    <p className="text-muted-foreground mb-1">Roll No</p>
                    <p className="font-semibold">{result.student.roll_no}</p>
                  </div>
                  <div className="w-px bg-border" />
                  <div className="text-center">
                    <p className="text-muted-foreground mb-1">Adm No</p>
                    <p className="font-semibold">{result.student.id}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3 border-b border-border">
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <AlertCircle className="size-4 text-rose-500" /> Pending Reminders
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <p className="text-xs text-muted-foreground mb-2">Transport fee is overdue by 12 days. System generated a late penalty of ₹100.</p>
                <Button variant="outline" size="sm" className="w-full text-xs">Send Reminder SMS</Button>
              </CardContent>
            </Card>
          </div>

          {/* Right: Fee Items & Cart */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-border bg-muted/10">
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <Receipt className="size-4" /> Outstanding Unpaid Fees
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-border">
                  {result.fees.filter(f => f.status !== 'PAID').map((fee) => {
                    const isSelected = selectedFees.has(fee.id)
                    return (
                      <div 
                        key={fee.id} 
                        className={`flex items-center gap-4 p-4 cursor-pointer transition-colors hover:bg-muted/20 ${isSelected ? 'bg-primary/5' : ''}`}
                        onClick={() => toggleFee(fee.id)}
                      >
                        <div className={`flex shrink-0 items-center justify-center size-5 rounded border ${isSelected ? 'bg-primary border-primary text-primary-foreground' : 'border-input bg-background'}`}>
                          {isSelected && <CheckCircle2 className="size-3.5" />}
                        </div>
                        <div className="flex-1">
                          <p className={`text-sm font-semibold ${isSelected ? 'text-foreground' : 'text-foreground/80'}`}>{fee.name}</p>
                          <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                            <span>Due: {formatDate(fee.due_date)}</span>
                            {fee.status === 'PARTIAL' && <span className="text-amber-500 font-medium">Partial Paid: {formatCurrency(fee.paid_amount)}</span>}
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`font-bold ${isSelected ? 'text-primary' : 'text-foreground/70'}`}>
                            {formatCurrency(fee.amount - fee.paid_amount)}
                          </p>
                        </div>
                      </div>
                    )
                  })}
                  {result.fees.filter(f => f.status !== 'PAID').length === 0 && (
                    <div className="p-8 text-center text-muted-foreground">No pending fees.</div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row items-center gap-6 justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground uppercase tracking-wider font-semibold mb-1">Total Collection Amount</p>
                    <p className="text-4xl font-black text-emerald-400 font-mono tracking-tight">{formatCurrency(totalToPay)}</p>
                    <p className="text-xs text-muted-foreground mt-2">Will generate automated receipt against {selectedFees.size} items.</p>
                  </div>
                  
                  <div className="w-full sm:w-auto space-y-3">
                    <Button 
                      className="w-full sm:w-48 h-12 text-base gap-2 shadow-emerald-500/20 shadow-lg bg-emerald-600 hover:bg-emerald-500"
                      disabled={totalToPay === 0 || isProcessing}
                      onClick={handleCollect}
                      loading={isProcessing}
                    >
                      <Wallet className="size-5" /> Collect & Print
                    </Button>
                    <div className="flex justify-center gap-3 text-muted-foreground">
                      <Banknote className="size-5 hover:text-foreground cursor-pointer" title="Cash" />
                      <CreditCard className="size-5 hover:text-foreground cursor-pointer" title="Card" />
                      <div className="font-bold text-xs px-2 py-0.5 border border-border rounded flex items-center justify-center hover:bg-muted cursor-pointer" title="UPI">UPI</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}
