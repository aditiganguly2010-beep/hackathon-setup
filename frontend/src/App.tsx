import { QueryClient, QueryClientProvider } from 'react-query'
import Dashboard from './components/Dashboard'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen">
        <Dashboard />
      </div>
    </QueryClientProvider>
  )
}

export default App
