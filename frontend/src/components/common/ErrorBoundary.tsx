import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Props {
  children?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined })
    window.location.reload()
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-background text-center px-4">
          <div className="bg-rose-500/10 border border-rose-500/20 p-6 rounded-3xl mb-6">
            <AlertTriangle className="w-16 h-16 text-rose-500" />
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-3 tracking-tight">Something went wrong</h1>
          <p className="text-muted-foreground mb-8 max-w-md">
            The application encountered an unexpected error. Please try refreshing the page.
          </p>
          {this.state.error && (
             <div className="w-full max-w-lg mb-8 bg-muted/30 border border-border rounded-lg p-4 text-left overflow-auto max-h-48">
                <code className="text-xs text-rose-400 font-mono">
                  {this.state.error.message}
                </code>
             </div>
          )}
          <Button onClick={this.handleReset} size="lg" className="w-48 shadow-lg shadow-primary/20">
            <RefreshCw className="mr-2 size-4" /> Refresh Page
          </Button>
        </div>
      )
    }

    return this.props.children
  }
}
