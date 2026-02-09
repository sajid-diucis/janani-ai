import { Suspense } from "react"
import { JananiDashboard } from "@/components/janani-dashboard"

// Loading fallback for Suspense boundary
function DashboardLoading() {
  return (
    <div className="flex h-screen items-center justify-center bg-gradient-to-br from-pink-50 to-purple-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500 mx-auto mb-4"></div>
        <p className="text-pink-600 font-medium">জানানী লোড হচ্ছে... / Loading Janani...</p>
      </div>
    </div>
  )
}

export default function Home() {
  // Suspense boundary required for useSearchParams() in JananiDashboard
  return (
    <Suspense fallback={<DashboardLoading />}>
      <JananiDashboard />
    </Suspense>
  )
}
