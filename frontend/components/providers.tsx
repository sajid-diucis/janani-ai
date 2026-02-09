
"use client"

"use client"

import { AuthProvider } from "@/context/auth-context"

// import { useRouter } from "next/navigation"
import { useState, useEffect } from "react"

export function Providers({ children }: { children: React.ReactNode }) {
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
    }, [])

    if (!mounted) {
        return <div className="flex h-screen items-center justify-center">Loading...</div>
    }

    // const router = useRouter()
    return (
        <AuthProvider>
            {children}
        </AuthProvider>
    )
}
