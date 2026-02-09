"use client"

import { useToast } from "@/hooks/use-toast"
import { useCallback } from "react"

/**
 * AGENTIC ACTION HANDLER
 * 
 * This hook processes backend responses that include tool execution data.
 * It does NOT navigate - the backend executes tools and returns data directly.
 * The main dashboard component uses this data to update state.
 */
export const useAgentAction = () => {
    const { toast } = useToast()

    const handleAgentResponse = useCallback((response: any): string => {
        // Handle both object and string inputs
        const message = typeof response === 'string'
            ? response
            : (response.message || response.response || "")

        console.log("🧠 Agent Response Received")

        // Check if backend already executed a tool (TRUE AGENTIC)
        const toolExecuted = response.tool_executed
        const toolData = response.tool_data

        if (toolExecuted && toolData) {
            console.log("🤖 BACKEND TOOL EXECUTED:", toolExecuted)
            // The data is already in the response - no navigation needed!
            // The janani-dashboard.tsx will use this data directly via:
            // setFoodPlan(toolData.menu_items) or setCarePlan(toolData)

            // Just show a toast to confirm the action
            switch (toolExecuted) {
                case "GENERATE_FOOD_MENU":
                    toast({
                        title: "🤖 মেনু তৈরি হয়েছে! / Menu Generated!",
                        description: "AI স্বয়ংক্রিয়ভাবে খাবারের তালিকা তৈরি করেছে।",
                    })
                    break
                case "GET_CARE_PLAN":
                    toast({
                        title: "🤖 কেয়ার প্ল্যান তৈরি! / Care Plan Ready!",
                        description: "AI সাপ্তাহিক পরিকল্পনা তৈরি করেছে।",
                    })
                    break
                case "CHECK_FOOD_SAFETY":
                    toast({
                        title: "🤖 খাবার পরীক্ষা সম্পন্ন / Food Checked!",
                        description: "AI খাবারের নিরাপত্তা যাচাই করেছে।",
                    })
                    break
            }
        }

        // For emergency (not yet agentic), still redirect
        if (response.emergency_activated) {
            toast({
                title: "🚨 জরুরি অবস্থা / Emergency!",
                description: "AR ড্যাশবোর্ডে নিয়ে যাওয়া হচ্ছে...",
                variant: "destructive",
            })
            setTimeout(() => {
                window.location.href = "http://localhost:8000/ar-dashboard"
            }, 500)
        }

        // Return clean message (without any action tags)
        return message.replace(/\[ACTION:\s*[^\]]+\]/g, "").trim()
    }, [toast])

    return { handleAgentResponse }
}
