import { PageHeader } from '@/components/common/PageHeader'
import { EmptyState } from '@/components/common/EmptyState'

export default function SchoolProfilePage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader 
        title="SchoolProfile" 
        description="This page is under construction." 
      />
      <EmptyState 
        title="Coming Soon" 
        description="The features for this module are currently being developed." 
      />
    </div>
  )
}
