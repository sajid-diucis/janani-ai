"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import {
  Home,
  Utensils,
  Mic,
  AlertCircle,
  Phone,
  ShoppingBag,
  Upload,
  CheckCircle,
  XCircle,
  Calendar,

  User,
  Camera,
  AlertTriangle,
  StopCircle,
  Send,
  Volume2,
  FileText,
  Stethoscope,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { CheckupCountdown } from "@/components/checkup-countdown"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { useAuth } from "@/context/auth-context"
import { useAgentAction } from "@/hooks/use-agent-action" // [NEW] Import
import { offlineManager } from "@/lib/offline-manager"
import { LoginPage } from "@/components/login-page"
import { VoiceResultCard } from "@/components/voice-result-card"

const API_BASE_URL = "http://localhost:8000"

type Tab = "home" | "nutrition"

interface FoodItem {
  name_bengali: string
  name_english: string
  price_bdt: number
  calories: number
  protein_g: number
  benefits_key: string
  image_url?: string
  recipe_bengali?: string
  audio_script_bengali?: string
  phase: number
}

interface TriageResult {
  risk_level: "High" | "Medium" | "Low"
  immediate_action_bengali: string
  primary_concern_bengali: string
  advice_bengali?: string
}

interface CarePlanItem {
  item_id: string
  title_bengali: string
  description_bengali: string
  category: string
  priority: string
  completed: boolean
}

interface CarePlan {
  week_number: number
  week_summary_bengali?: string
  baby_development_bengali?: string
  mother_changes_bengali?: string
  weekly_checklist: CarePlanItem[]
  nutrition_focus: string[]
  foods_to_emphasize: string[]
  warning_signs: Array<{
    sign_bengali: string
    is_emergency: boolean
  }>
}

interface FoodSafetyResult {
  safe: boolean
  reason_bengali: string
  alternatives_bengali?: string[]
  is_caution?: boolean
}

const causalData = {
  step1_anomalies: [
    { vital: "Blood Pressure", value: "160/110 mmHg", baseline: "120/80", status: "ELEVATED" },
    { vital: "Protein in Urine", value: "2+", baseline: "Negative", status: "ABNORMAL" },
    { vital: "Edema", value: "Severe", onset: "Week 36", status: "ABNORMAL" },
  ],
  step2_timeline: [
    { week: 12, event: "Mild headache", severity: "low" },
    { week: 36, event: "Edema started", severity: "medium" },
    { week: 38, event: "BP began rising", severity: "high" },
    { week: 40, event: "Protein appeared", severity: "critical" },
  ],
  step3_mechanisms: [
    { from: "High BP", mechanism: "Damages blood vessels" },
    { from: "Vessel damage", mechanism: "Protein leaks to urine" },
    { from: "Protein loss", mechanism: "Kidney stress" },
  ],
  step4_diagnosis: [
    { condition: "Preeclampsia", probability: "85%", severity: "critical" },
    { condition: "Chronic Hypertension", probability: "10%", severity: "medium" },
  ],
  step5_recommendation: {
    action: "URGENT TRANSFER REQUIRED",
    timeframe: "Within 2 hours",
    facility: "Level 3 hospital",
    who_reference: "Section 4.2.1, Page 87",
  },
}

const getCausalSeverityClass = (severity: string) => {
  switch (severity) {
    case "low":
      return "bg-green-100 text-green-700 border-green-200"
    case "medium":
      return "bg-amber-100 text-amber-700 border-amber-200"
    case "high":
      return "bg-orange-100 text-orange-700 border-orange-200"
    case "critical":
      return "bg-red-100 text-red-700 border-red-200"
    default:
      return "bg-slate-100 text-slate-600 border-slate-200"
  }
}

export function JananiDashboard() {
  const { user, logout, isLoading } = useAuth()

  const currentUserId = user?.id || "guest"
  const { toast } = useToast()
  const { handleAgentResponse } = useAgentAction() // [NEW] Initialize Hook
  const [activeTab, setActiveTab] = useState<Tab>("home")

  // Profile state
  const [age, setAge] = useState("")
  const [weekOfPregnancy, setWeekOfPregnancy] = useState("")
  const [weight, setWeight] = useState("")
  const [gravida, setGravida] = useState("")

  // Home tab - Voice health check
  const [isRecording, setIsRecording] = useState(false)
  const [transcribedText, setTranscribedText] = useState("")
  const [triageResult, setTriageResult] = useState<TriageResult | null>(null)
  const [loadingTriage, setLoadingTriage] = useState(false)
  const [showCausalLogic, setShowCausalLogic] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const [chatInput, setChatInput] = useState("")
  // [NEW] Real-time processing step indicator
  type ProcessingStep = "idle" | "uploading" | "transcribing" | "ai" | "audio" | "done" | "error"
  const [processingStep, setProcessingStep] = useState<ProcessingStep>("idle")

  // Weekly care plan
  const [carePlan, setCarePlan] = useState<CarePlan | null>(null)
  const [loadingCarePlan, setLoadingCarePlan] = useState(false)

  // Nutrition state - Menu Generator
  const [trimester, setTrimester] = useState("second")
  const [budget, setBudget] = useState("2000")
  const [conditions, setConditions] = useState<string[]>([])
  const [foodItems, setFoodItems] = useState<FoodItem[]>([])
  const [loadingFood, setLoadingFood] = useState(false)
  const [currentPhase, setCurrentPhase] = useState(1)
  const [selectedFoodItem, setSelectedFoodItem] = useState<FoodItem | null>(null)

  // Food Safety Check
  const [foodCheckInput, setFoodCheckInput] = useState("")
  const [foodSafetyResult, setFoodSafetyResult] = useState<FoodSafetyResult | null>(null)
  const [loadingFoodCheck, setLoadingFoodCheck] = useState(false)

  // Document Upload
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploadingDoc, setUploadingDoc] = useState(false)
  // DEV: Simulate Offline Mode
  const [simulateOffline, setSimulateOffline] = useState(false)
  const [isRealOffline, setIsRealOffline] = useState(false)
  const isOffline = isRealOffline || simulateOffline

  // Clinical Report State
  const [clinicalReport, setClinicalReport] = useState<any>(null)
  const [loadingReport, setLoadingReport] = useState(false)

  // [NEW] Voice Tool Results - For inline display
  interface VoiceToolResult {
    toolExecuted: string | null
    toolResult: any
    aiResponse: string
  }
  const [voiceToolResult, setVoiceToolResult] = useState<VoiceToolResult | null>(null)

  useEffect(() => {
    setIsRealOffline(!navigator.onLine)
    window.addEventListener('online', () => setIsRealOffline(false))
    window.addEventListener('offline', () => setIsRealOffline(true))
  }, [])

  const searchParams = useSearchParams()

  // [NEW] Query Parameter-based Tab Switcher (String-Based Architecture)
  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab === 'nutrition') {
      setActiveTab('nutrition')
    } else if (tab === 'care-plan') {
      setActiveTab('home')
      setTimeout(() => {
        const section = document.getElementById('care-plan-section')
        if (section) section.scrollIntoView({ behavior: 'smooth' })
      }, 500)
    }
  }, [searchParams])

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>
  }

  if (!user) {
    return <LoginPage />
  }

  const handleSaveProfile = async () => {
    if (!age || !weekOfPregnancy || !weight || !gravida) {
      toast({
        title: "তথ্য অনুপস্থিত / Missing Information",
        description: "দয়া করে সব তথ্য পূরণ করুন / Please fill all fields",
        variant: "destructive",
      })
      return
    }

    const gravidaMap: Record<string, number> = {
      "first": 1,
      "second": 2,
      "third": 3,
      "fourth": 4
    }

    try {
      await fetch(`${API_BASE_URL}/api/midwife/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUserId,
          name: user?.name || "মা",
          age: Number.parseInt(age),
          current_week: Number.parseInt(weekOfPregnancy),
          current_weight_kg: Number.parseFloat(weight),
          gravida: gravidaMap[gravida] || 1,
        }),
      })

      toast({
        title: "প্রোফাইল সংরক্ষিত / Profile Saved",
        description: "আপনার তথ্য সফলভাবে সংরক্ষণ করা হয়েছে / Your information has been saved",
      })

      // Refresh plan after saving profile
      handleGetCarePlan()
    } catch (error) {
      toast({
        title: "ত্রুটি / Error",
        description: "প্রোফাইল সংরক্ষণ করা যায়নি / Failed to save profile",
        variant: "destructive",
      })
      console.error("[v0] Profile save error:", error)
    }
  }

  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      const chunks: Blob[] = []

      recorder.ondataavailable = (e) => {
        chunks.push(e.data)
      }

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: "audio/webm" })
        await handleTranscribe(audioBlob)
        stream.getTracks().forEach((track) => track.stop())
      }

      setMediaRecorder(recorder)
      recorder.start()
      setIsRecording(true)

      toast({
        title: "রেকর্ডিং শুরু / Recording Started",
        description: "এখন আপনার লক্ষণ বলুন / Speak your symptoms now",
      })
    } catch (error) {
      toast({
        title: "মাইক্রোফোন ত্রুটি / Microphone Error",
        description: "আবার চেষ্টা করুন / Could not hear you, try again",
        variant: "destructive",
      })
      console.error("[v0] Microphone error:", error)
    }
  }

  const handleStopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop()
      setIsRecording(false)
    }
  }

  const handleTranscribe = async (audioBlob: Blob) => {
    try {
      const formData = new FormData()
      formData.append("audio", audioBlob, "recording.webm")
      formData.append("user_id", currentUserId) // Pass user ID for context

      setProcessingStep("transcribing") // Step 1: Transcribing

      // [NEW] Use the new Voice Health Check endpoint with full agentic capabilities
      const response = await fetch(`${API_BASE_URL}/api/voice/health-check`, {
        method: "POST",
        body: formData,
      })

      setProcessingStep("ai") // Step 2: AI Processing

      const data = await response.json()

      // Get transcription
      const text = data.transcription || ""
      setTranscribedText(text)

      // [NEW] Emergency Redirect Check
      if (data.emergency_activated && data.emergency_redirect) {
        setProcessingStep("done")

        // [FIX] Show the result card immediately so user sees "Calling Ambulance"
        setVoiceToolResult({
          toolExecuted: "ACTIVATE_EMERGENCY",
          toolResult: data.tool_result,
          aiResponse: data.response || "Emergency Activated"
        })

        toast({
          title: "🚨 জরুরি অবস্থা শনাক্ত হয়েছে!",
          description: "আপনাকে ইমার্জেন্সি ড্যাশবোর্ডে নিয়ে যাওয়া হচ্ছে...",
          variant: "destructive",
          className: "bg-red-600 text-white border-none"
        })
        // Delay slightly for user to see toast
        setTimeout(() => {
          window.location.href = data.emergency_redirect
        }, 1500)
        return
      }

      if (!data.success) {
        setProcessingStep("error")
        toast({
          title: "ট্রান্সক্রিপশন ত্রুটি / Transcription Error",
          description: data.error || "Please try again",
          variant: "destructive",
        })
        return
      }

      // [AGENTIC] Check if a tool was executed by the voice endpoint
      // Now display results INLINE instead of switching tabs
      if (data.tool_executed) {
        console.log("🤖 Voice executed tool:", data.tool_executed, data.tool_result)

        // [NEW] Set inline result for display in same page
        setVoiceToolResult({
          toolExecuted: data.tool_executed,
          toolResult: data.tool_result,
          aiResponse: data.response || ""
        })

        // Also update specific state for profile updates
        if (data.tool_executed === "UPDATE_PROFILE" && data.tool_result) {
          const updated = data.tool_result
          if (updated.weeks_pregnant) setWeekOfPregnancy(String(updated.weeks_pregnant))
          if (updated.age) setAge(String(updated.age))
        }

        toast({
          title: `🤖 ${data.tool_executed === "GENERATE_FOOD_MENU" ? "মেনু তৈরি হয়েছে!"
            : data.tool_executed === "GET_CARE_PLAN" ? "কেয়ার প্ল্যান প্রস্তুত!"
              : data.tool_executed === "UPDATE_PROFILE" ? "প্রোফাইল আপডেট!"
                : "সম্পন্ন!"}`,
          description: "নিচে ফলাফল দেখুন / See results below",
        })
      } else if (data.response) {
        // No tool executed - just AI response
        setVoiceToolResult({
          toolExecuted: null,
          toolResult: null,
          aiResponse: data.response
        })
      }

      // Play audio if available
      if (data.response) {
        setProcessingStep("audio") // Step 3: Audio Generation
        if (data.audio_base64) {
          try {
            const audioData = Uint8Array.from(atob(data.audio_base64), c => c.charCodeAt(0))
            const blob = new Blob([audioData], { type: "audio/mp3" })
            const audio = new Audio(URL.createObjectURL(blob))
            await audio.play()
          } catch (e) {
            await playAudio(data.response)
          }
        } else {
          await playAudio(data.response)
        }
      } else if (text) {
        // Fallback to old triage if no AI response
        await handleTriage(text)
      }

      setProcessingStep("done") // Done

    } catch (error) {
      setProcessingStep("error")
      toast({
        title: "ট্রান্সক্রিপশন ত্রুটি / Transcription Error",
        description: "আবার চেষ্টা করুন / Please try again",
        variant: "destructive",
      })
      console.error("[v0] Voice Health Check error:", error)
    }
  }


  const playAudio = async (text: string, forceOffline: boolean = false) => {
    // 1. Check for Bengali voice in browser
    const voices = typeof window !== "undefined" && "speechSynthesis" in window
      ? window.speechSynthesis.getVoices()
      : []
    const bengaliVoice = voices.find(v => v.lang.includes("bn"))

    // 2. If Bengali voice exists AND (offline OR forceOffline), use browser TTS
    if (bengaliVoice && (isOffline || forceOffline)) {
      console.log("[Audio] Using Browser TTS (Bengali voice found)")
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.voice = bengaliVoice
      utterance.lang = bengaliVoice.lang
      utterance.rate = 1.0
      utterance.pitch = 1.0
      window.speechSynthesis.speak(utterance)
      return
    }

    // 3. Online Mode: Use Server API (gTTS) for Bengali audio
    // This is the PRIMARY path since browser likely has no Bengali voice
    try {
      console.log("[Audio] Using Server gTTS API (No Bengali voice in browser)")
      const response = await fetch(`${API_BASE_URL}/api/voice/speak?t=${Date.now()}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          language: "bn",
        }),
      })

      if (!response.ok) throw new Error("TTS API Failed")

      const blob = await response.blob()
      const audio = new Audio(URL.createObjectURL(blob))
      await audio.play()
    } catch (error: any) {
      console.error("TTS Server Error:", error)

      // 4. Ultimate Fallback: Try browser with any available voice
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        console.log("[Audio] Server failed, attempting browser fallback")
        window.speechSynthesis.cancel()
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.lang = "bn-BD"
        // Try any Google voice as a last resort
        const anyVoice = voices.find(v => v.name.includes("Google")) || voices[0]
        if (anyVoice) utterance.voice = anyVoice
        window.speechSynthesis.speak(utterance)
      } else {
        toast({
          title: "অডিও ত্রুটি / Audio Error",
          description: "অডিও প্লে করা যাচ্ছে না / Could not play audio",
          variant: "destructive",
        })
      }
    }
  }

  const handleTriage = async (text: string) => {
    // 0. IMMEDIATE OFFLINE CHECK
    if (isOffline) {
      console.log("Offline mode detected. Checking local rules...")
      const offlineResp = offlineManager.getOfflineResponse(text)

      if (offlineResp) {
        const mockResult: TriageResult = {
          risk_level: "Medium",
          immediate_action_bengali: offlineResp,
          primary_concern_bengali: "অফলাইন মোড / Offline Mode",
          advice_bengali: "ইন্টারনেট নেই, তাই সংরক্ষিত তথ্য দেখানো হচ্ছে। জরুরি হলে ১৬২৬৩ নম্বরে কল করুন।"
        }
        setTriageResult(mockResult)

        // Speak offline response
        await playAudio(offlineResp, true)

        toast({
          title: "অফলাইন মোড / Offline Mode",
          description: "ইন্টারনেট নেই, তাই সংরক্ষিত তথ্য দেখানো হচ্ছে।",
          variant: "default",
        })
        return // STOP HERE. Do not try API.
      }
    }

    setLoadingTriage(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/midwife/triage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUserId,
          input_text: text,
          include_history: true,
        }),
      })

      const data = await response.json()

      // [NEW] Universal Action Handler
      // This will check for "emergency_activated" and redirect if needed
      // It also returns the text we should display
      const resultData = data.data?.triage_result || data.triage_result

      // Pass the WHOLE data object to the handler.
      // It returns the "Clean Message" (without [ACTION: TAGS])
      const cleanAIResponse = handleAgentResponse(data)

      // =======================================================================
      // AGENTIC TOOL EXECUTION: Check if backend executed a tool for us
      // =======================================================================
      const toolExecuted = data.tool_executed
      const toolData = data.tool_data

      if (toolExecuted) {
        console.log("🤖 AGENTIC TOOL EXECUTED:", toolExecuted, toolData)

        // If menu was generated, populate the food plan
        if (toolExecuted === "GENERATE_FOOD_MENU" && toolData?.menu_items) {
          setFoodItems(toolData.menu_items)
          setActiveTab("nutrition") // Auto-switch to nutrition tab
          toast({
            title: "🤖 AI সক্রিয়ভাবে মেনু তৈরি করেছে!",
            description: `${toolData.menu_items.length}টি খাবার তৈরি হয়েছে। Nutrition ট্যাবে দেখুন।`,
          })
        }

        // If care plan was generated
        if (toolExecuted === "GET_CARE_PLAN" && toolData) {
          setCarePlan(toolData)
          setActiveTab("home")
          toast({
            title: "🤖 AI সক্রিয়ভাবে কেয়ার প্ল্যান তৈরি করেছে!",
            description: "আপনার সাপ্তাহিক পরামর্শ প্রস্তুত।",
          })
        }
      }

      const responseText = cleanAIResponse || resultData?.advice_bengali || resultData?.immediate_action_bengali || ""

      const isSoftError =
        responseText.includes("Error:") ||
        responseText.includes("Connection error") ||
        responseText.includes("AI সেবা")

      if (isSoftError) {
        console.log("Server returned AI Error. Switching to Offline Mode Forcefully.")
        throw new Error("AI_CONNECTION_FAILURE")
      }

      setTriageResult(resultData || null)

      toast({
        title: "মূল্যায়ন সম্পন্ন / Assessment Complete",
        description: "আপনার স্বাস্থ্য পরীক্ষার ফলাফল প্রস্তুত / Your health check results are ready",
      })

      // Auto-play audio response
      if (resultData?.response_audio_text) {
        await playAudio(resultData.response_audio_text)
      } else if (resultData?.immediate_action_bengali) {
        await playAudio(resultData.immediate_action_bengali)
      }
    } catch (error: any) {
      console.error("[v0] Triage error:", error)

      // Offline Fallback logic (Triggered by Network Error OR Soft Error)
      const offlineResp = offlineManager.getOfflineResponse(text)

      if (offlineResp) {
        console.log("Using Offline Fallback for:", text)
        const mockResult: TriageResult = {
          risk_level: "Medium",
          immediate_action_bengali: offlineResp,
          primary_concern_bengali: "অফলাইন মোড / Offline Mode",
          advice_bengali: "ইন্টারনেট নেই, তাই সংরক্ষিত তথ্য দেখানো হচ্ছে। জরুরি হলে ১৬২৬৩ নম্বরে কল করুন।"
        }
        setTriageResult(mockResult)

        // Speak offline response
        await playAudio(offlineResp, true)

        toast({
          title: "অফলাইন মোড / Offline Mode",
          description: "ইন্টারনেট সমস্যা। অফলাইন উত্তর দেখানো হচ্ছে।",
          variant: "default",
        })
        return
      }

      toast({
        title: "মূল্যায়ন ত্রুটি / Assessment Error",
        description: "সার্ভারে সংযোগ করা যাচ্ছে না এবং অফলাইন উত্তর পাওয়া যায়নি।",
        variant: "destructive",
      })
    } finally {
      setLoadingTriage(false)
    }
  }

  const handleChatSubmit = async () => {
    if (!chatInput.trim()) return

    const inputText = chatInput.trim()
    setTranscribedText(inputText) // Show what user typed in the "You said" box
    setChatInput("")
    setLoadingTriage(true)
    setVoiceToolResult(null) // Clear previous result

    try {
      // [NEW] Call the same AI agent that voice uses but with text input
      const response = await fetch(`${API_BASE_URL}/api/midwife/triage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUserId,
          input_text: inputText,
          include_history: true,
        }),
      })

      const data = await response.json()
      console.log("Chat response:", data)

      const triageData = data.triage_result || data.data?.triage_result

      // Check if tool was executed by the backend
      if (data.tool_executed) {
        console.log("🤖 Chat executed tool:", data.tool_executed, data.tool_data)

        // Set inline result for display
        setVoiceToolResult({
          toolExecuted: data.tool_executed,
          toolResult: data.tool_data,
          aiResponse: data.ai_response || triageData?.immediate_action_bengali || ""
        })

        toast({
          title: `🤖 ${data.tool_executed === "GENERATE_FOOD_MENU" ? "মেনু তৈরি হয়েছে!"
            : data.tool_executed === "GET_CARE_PLAN" ? "কেয়ার প্ল্যান প্রস্তুত!"
              : data.tool_executed === "UPDATE_PROFILE" ? "প্রোফাইল আপডেট!"
                : "সম্পন্ন!"}`,
          description: "নিচে ফলাফল দেখুন / See results below",
        })
      } else {
        // No tool - just AI response
        const aiResponse = handleAgentResponse(data) || triageData?.immediate_action_bengali || ""

        setVoiceToolResult({
          toolExecuted: null,
          toolResult: null,
          aiResponse: aiResponse
        })

        toast({
          title: "মূল্যায়ন সম্পন্ন / Assessment Complete",
          description: "আপনার স্বাস্থ্য পরীক্ষার ফলাফল প্রস্তুত",
        })
      }

      // Play audio for the response
      const audioText = data.ai_response || triageData?.immediate_action_bengali
      if (audioText) {
        await playAudio(audioText)
      }

    } catch (error) {
      console.error("[v0] Chat submit error:", error)
      toast({
        title: "ত্রুটি / Error",
        description: "সার্ভারে সংযোগ করা যাচ্ছে না",
        variant: "destructive",
      })
    } finally {
      setLoadingTriage(false)
    }
  }

  const handleGetCarePlan = async () => {
    const week = weekOfPregnancy || "20"
    setLoadingCarePlan(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/midwife/care-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUserId,
          week_number: Number.parseInt(week),
        }),
      })

      const data = await response.json()
      // Extract from the .care_plan property in the response
      const plan = data.data?.care_plan || data.care_plan
      setCarePlan(plan || null)

      if (plan) {
        toast({
          title: "যত্ন পরিকল্পনা প্রস্তুত / Care Plan Ready",
          description: `সপ্তাহ ${plan.week_number} এর পরিকল্পনা লোড হয়েছে`,
        })
      }
    } catch (error) {
      toast({
        title: "ত্রুটি / Error",
        description: "পরিকল্পনা লোড করা যায়নি / Failed to load care plan",
        variant: "destructive",
      })
      console.error("[v0] Care plan error:", error)
    } finally {
      setLoadingCarePlan(false)
    }
  }

  const handleConditionToggle = (condition: string) => {
    setConditions((prev) => (prev.includes(condition) ? prev.filter((c) => c !== condition) : [...prev, condition]))
  }

  const fetchFoodPlan = async (phase: number) => {
    setLoadingFood(true)
    try {
      // Ensure profile is updated before getting recommendations
      await fetch(`${API_BASE_URL}/api/food/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUserId,
          trimester,
          conditions,
          budget_weekly_bdt: Number.parseFloat(budget),
        }),
      })

      const response = await fetch(`${API_BASE_URL}/api/food/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUserId,
          budget_weekly: Number.parseFloat(budget),
          phase: phase
        }),
      })

      const data = await response.json()
      const newItems = data.items || data.recommendations || []

      // Always REPLACE old items with new ones
      setFoodItems(newItems)
      setCurrentPhase(phase)

      toast({
        title: phase === 1 ? "খাদ্য পরিকল্পনা প্রস্তুত / Food Plan Ready" : "নতুন মেনু লোড হয়েছে / New Menu Loaded",
        description: `পর্যায় ${phase} সম্পন্ন / Phase ${phase} complete`,
      })
    } catch (error) {
      toast({
        title: "ত্রুটি / Error",
        description: "খাদ্য পরিকল্পনা পাওয়া যায়নি / Failed to get food plan",
        variant: "destructive",
      })
      console.error("[v0] Food plan error:", error)
    } finally {
      setLoadingFood(false)
    }
  }

  const handleGetFoodPlan = async () => {
    if (!trimester || !budget) {
      toast({
        title: "তথ্য অনুপস্থিত / Missing Information",
        description: "ত্রৈমাসিক এবং বাজেট নির্বাচন করুন / Please select trimester and enter budget",
        variant: "destructive",
      })
      return
    }
    await fetchFoodPlan(1)
  }

  const handleLoadMoreItems = async () => {
    // Support for 4 phases now: 1 (7 items), 2 (4 items), 3 (4 items), 4 (AI generated)
    if (currentPhase < 4) {
      await fetchFoodPlan(currentPhase + 1)
    }
  }

  const handlePlayAudioScript = async (text: string) => {
    await playAudio(text)
  }

  const handleFoodSafetyCheck = async () => {
    if (!foodCheckInput.trim()) {
      toast({
        title: "তথ্য অনুপস্থিত / Missing Information",
        description: "খাবারের নাম লিখুন / Please enter a food name",
        variant: "destructive",
      })
      return
    }

    setLoadingFoodCheck(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/food/check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "web",
          food_name: foodCheckInput,
        }),
      })

      const data = await response.json()
      setFoodSafetyResult(data.data?.safety_result || data || null)

      toast({
        title: "পরীক্ষা সম্পন্ন / Check Complete",
        description: data.safe ? "নিরাপদ খাবার / Safe to eat" : "এড়িয়ে চলুন / Avoid this food",
      })
    } catch (error) {
      toast({
        title: "ত্রুটি / Error",
        description: "খাবার পরীক্ষা করা যায়নি / Failed to check food",
        variant: "destructive",
      })
      console.error("[v0] Food check error:", error)
    } finally {
      setLoadingFoodCheck(false)
    }
  }

  const handleFoodImageCheck = async (file: File) => {
    setLoadingFoodCheck(true)
    try {
      const formData = new FormData()
      formData.append("image", file)
      formData.append("user_id", "web")

      const response = await fetch(`${API_BASE_URL}/api/food/quick-check`, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()
      setFoodSafetyResult(data.data?.safety_result || data || null)

      toast({
        title: "ছবি বিশ্লেষণ সম্পন্ন / Image Analysis Complete",
        description: data.safe ? "নিরাপদ খাবার / Safe to eat" : "এড়িয়ে চলুন / Avoid this food",
      })
    } catch (error) {
      toast({
        title: "ত্রুটি / Error",
        description: "ছবি পরীক্ষা করা যায়নি / Failed to check image",
        variant: "destructive",
      })
      console.error("[v0] Food image check error:", error)
    } finally {
      setLoadingFoodCheck(false)
    }
  }

  const handleDocumentUpload = async (file: File) => {
    setUploadingDoc(true)
    try {
      const formData = new FormData()
      formData.append("document", file)
      formData.append("user_id", "web")

      const response = await fetch(`${API_BASE_URL}/api/profile/upload-document`, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      // Auto-fill profile fields based on document
      if (data.extracted_info) {
        if (data.extracted_info.has_anemia && !conditions.includes("anemia")) {
          setConditions((prev) => [...prev, "anemia"])
        }
        if (data.extracted_info.has_diabetes && !conditions.includes("diabetes")) {
          setConditions((prev) => [...prev, "diabetes"])
        }
      }

      setUploadedFile(file)
      toast({
        title: "নথি আপলোড সফল / Document Uploaded",
        description: "প্রোফাইল স্বয়ংক্রিয়ভাবে আপডেট করা হয়েছে / Profile auto-filled",
      })
    } catch (error) {
      toast({
        title: "ত্রুটি / Error",
        description: "নথি আপলোড করা যায়নি / Failed to upload document",
        variant: "destructive",
      })
      console.error("[v0] Document upload error:", error)
    } finally {
      setUploadingDoc(false)
    }
  }

  const handleGenerateClinicalReport = async () => {
    setLoadingReport(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/midwife/clinical-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: currentUserId,
          include_vitals: true,
          vitals: {
            blood_pressure_systolic: 120, // Default or fetch from profile
            blood_pressure_diastolic: 80,
            hemoglobin: 11.5
          }
        }),
      })

      const data = await response.json()
      if (data.success && data.report) {
        setClinicalReport(data.report)
        toast({
          title: "রিপোর্ট প্রস্তুত / Report Ready",
          description: "ক্লিনিক্যাল রিপোর্ট তৈরি হয়েছে / Clinical report generated",
        })
      } else {
        throw new Error(data.error || "Failed to generate")
      }
    } catch (error) {
      toast({
        title: "ত্রুটি / Error",
        description: "রিপোর্ট তৈরি করা যায়নি / Could not generate report",
        variant: "destructive",
      })
      console.error("Report error:", error)
    } finally {
      setLoadingReport(false)
    }
  }

  const handleStartShopping = () => {
    window.open("https://www.google.com/maps/search/grocery+store+near+me", "_blank")
  }

  const handleEmergency = () => {
    // Stop any active usage in this tab first
    if (isRecording) {
      handleStopRecording()
    }
    // Small delay to ensure tracks are released
    setTimeout(() => {
      window.open(`${API_BASE_URL}/ar-dashboard`, "_blank")
    }, 200)
  }

  const handleCall = (number: string) => {
    window.location.href = `tel:${number}`
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case "High":
        return "bg-red-500 text-white"
      case "Medium":
        return "bg-orange-500 text-white"
      case "Low":
        return "bg-green-500 text-white"
      default:
        return "bg-gray-500 text-white"
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-secondary/5 pb-20">
      <div className="container mx-auto px-4 py-6 max-w-4xl">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex flex-col items-center">
          <div className="w-full flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <div className="bg-teal-100 p-2 rounded-full">
                <User className="w-5 h-5 text-teal-700" />
              </div>
              <span className="font-medium text-teal-900">{user?.name} ({user?.phone})</span>
            </div>
            <Button variant="outline" size="sm" onClick={logout} className="text-red-600 hover:text-red-700 hover:bg-red-50">
              লগআউট / Logout
            </Button>
          </div>

          {/* DEV: Offline Toggle */}
          <div className="flex items-center gap-2 mb-4">
            <Button
              variant={simulateOffline ? "destructive" : "outline"}
              size="sm"
              onClick={() => setSimulateOffline(!simulateOffline)}
            >
              {simulateOffline ? "Disable Offline Sim" : "Simulate Offline Mode"}
            </Button>
          </div>

          {(isOffline) && (
            <div className="mb-4 bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-2 rounded-full flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm font-medium">অফলাইন মোড (Offline Mode)</span>
            </div>
          )}
          <h1 className="text-4xl font-bold text-primary mb-2">Janani</h1>
          <p className="text-muted-foreground text-balance">আপনার বিশ্বস্ত ডিজিটাল সহায়ক / Your Trusted Digital Companion</p>
        </motion.div>

        <AnimatePresence mode="wait">
          {activeTab === "home" && (
            <motion.div
              key="home"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {/* Emergency & Triage */}
              <Card className="border-primary">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mic className="w-6 h-6" />
                    ভয়েস স্বাস্থ্য পরীক্ষা / Voice Health Check
                  </CardTitle>
                  <CardDescription>আপনার লক্ষণ বলুন এবং তাৎক্ষণিক পরামর্শ পান / Speak your symptoms</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col items-center gap-6">
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={isRecording ? handleStopRecording : handleStartRecording}
                    className={`w-32 h-32 rounded-full flex items-center justify-center ${isRecording ? "bg-destructive" : "bg-primary"
                      } text-primary-foreground shadow-lg`}
                  >
                    <motion.div
                      animate={isRecording ? { scale: [1, 1.2, 1] } : {}}
                      transition={{ repeat: Number.POSITIVE_INFINITY, duration: 1.5 }}
                    >
                      {isRecording ? <StopCircle className="h-12 w-12 text-white" /> : <Mic className="h-12 w-12 text-white" />}
                    </motion.div>
                  </motion.button>

                  {/* Real-time Processing Status */}
                  {(processingStep !== "idle" && processingStep !== "done" && processingStep !== "error") && (
                    <div className="mt-6 w-full max-w-xs space-y-4">
                      <div className="flex items-center justify-between text-sm font-medium text-slate-600">
                        <span className={processingStep === "transcribing" ? "text-primary animate-pulse" : "text-green-600"}>
                          {processingStep === "transcribing" ? "🎤 শুনছি..." : "✅ শোনা শেষ"}
                        </span>
                        <span className={processingStep === "ai" ? "text-primary animate-pulse" : (processingStep === "audio" ? "text-green-600" : "text-slate-400")}>
                          {processingStep === "ai" ? "🧠 ভাবছি..." : (processingStep === "audio" ? "✅ বিশ্লেষণ শেষ" : "বিশ্লেষণ")}
                        </span>
                        <span className={processingStep === "audio" ? "text-primary animate-pulse" : "text-slate-400"}>
                          {processingStep === "audio" ? "🔊 উত্তর দিচ্ছি..." : "উত্তর"}
                        </span>
                      </div>
                      <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary to-purple-600 transition-all duration-500 ease-in-out"
                          style={{
                            width: processingStep === "transcribing" ? "30%" :
                              processingStep === "ai" ? "60%" :
                                processingStep === "audio" ? "90%" : "0%"
                          }}
                        />
                      </div>
                      <p className="text-center text-xs text-slate-500 animate-pulse">
                        {processingStep === "transcribing" && "আপনার কথা টেক্সটে রূপান্তর করা হচ্ছে..."}
                        {processingStep === "ai" && "AI আপনার সমস্যার সমাধান খুঁজছে..."}
                        {processingStep === "audio" && "ভয়েস উত্তর তৈরি করা হচ্ছে..."}
                      </p>
                    </div>
                  )}

                  <p className="text-sm text-slate-500 mt-4 text-center max-w-sm">
                    {isRecording
                      ? "বলুন: 'আমার জ্বর এসেছে' বা 'এই সপ্তাহের কেয়ার প্ল্যান দাও'..."
                      : "রেকর্ডিং শুরু করতে ট্যাপ করুন / Tap to start recording"}
                  </p>
                  <div className="w-full relative flex items-center gap-2 opacity-50">
                    <div className="h-px bg-border flex-1" />
                    <span className="text-muted-foreground text-xs uppercase">অথবা লিখে জানান / OR TYPE</span>
                    <div className="h-px bg-border flex-1" />
                  </div>

                  <div className="flex w-full gap-2">
                    <Input
                      placeholder="সমস্যা লিখুন... (যেমন: আমার মাথা ব্যথা) / Type symptoms..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleChatSubmit()}
                    />
                    <Button onClick={handleChatSubmit} disabled={!chatInput.trim() || loadingTriage}>
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>

                  {transcribedText && (
                    <Card className="w-full bg-muted">
                      <CardContent className="pt-6">
                        <p className="text-sm font-medium mb-1">আপনি বলেছেন / You said:</p>
                        <p className="text-foreground">{transcribedText}</p>
                      </CardContent>
                    </Card>
                  )}

                  {/* [NEW] Inline Voice Tool Results - Menu, Care Plan, Profile, Food Safety */}
                  {voiceToolResult && (
                    <VoiceResultCard
                      toolExecuted={voiceToolResult.toolExecuted}
                      toolResult={voiceToolResult.toolResult}
                      aiResponse={voiceToolResult.aiResponse}
                      onPlayAudio={(text) => playAudio(text)}
                    />
                  )}

                  {(loadingTriage || triageResult) && (
                    <Card className="w-full">
                      <CardContent className="pt-6 space-y-4">
                        {loadingTriage ? (
                          <p className="text-center text-muted-foreground">
                            লক্ষণ বিশ্লেষণ করা হচ্ছে... / Analyzing symptoms...
                          </p>
                        ) : triageResult ? (
                          <>
                            <div>
                              <Label className="mb-2 block">ঝুঁকি স্তর / Risk Level</Label>
                              <Badge className={`${getRiskColor(triageResult.risk_level)} px-4 py-2 text-base`}>
                                {triageResult.risk_level}
                              </Badge>
                            </div>

                            <div>
                              <Label className="mb-2 block">প্রধান উদ্বেগ / Primary Concern</Label>
                              <Card className="bg-muted">
                                <CardContent className="pt-6">
                                  <p className="text-foreground">{triageResult.primary_concern_bengali}</p>
                                </CardContent>
                              </Card>
                            </div>

                            <div>
                              <Label className="mb-2 block">তাৎক্ষণিক পদক্ষেপ / Immediate Action</Label>
                              <Card className="bg-accent">
                                <CardContent className="pt-6">
                                  <p className="text-accent-foreground font-medium mb-4">
                                    {triageResult.immediate_action_bengali}
                                  </p>
                                  {/* MANUAL PLAY BUTTON For Robustness */}
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => playAudio(triageResult.immediate_action_bengali || "", true)}
                                    className="gap-2"
                                  >
                                    <Volume2 className="w-4 h-4" />
                                    শুনুন (Play Audio)
                                  </Button>
                                </CardContent>
                              </Card>
                            </div>

                            <div>
                              <Button
                                onClick={() => setShowCausalLogic((prev) => !prev)}
                                className="bg-[#2563eb] text-white hover:bg-[#1e4ed8] rounded-lg px-6 py-3"
                              >
                                🧠 Show Causal Logic
                              </Button>
                            </div>

                            {showCausalLogic && (
                              <div className="rounded-lg border border-slate-200 bg-slate-50 p-5 text-slate-900 space-y-6">
                                <div className="space-y-3">
                                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                                    STEP 1: ANOMALIES DETECTED
                                  </div>
                                  <ul className="space-y-2">
                                    {causalData.step1_anomalies.map((item, index) => (
                                      <li
                                        key={`${item.vital}-${index}`}
                                        className="rounded-md border border-slate-200 bg-white p-3 text-sm"
                                      >
                                        <div className="flex flex-wrap items-center justify-between gap-2">
                                          <span className="font-semibold">{item.vital}</span>
                                          <span className="text-slate-700">{item.value}</span>
                                        </div>
                                        <div className="mt-1 text-xs text-slate-500">
                                          {item.baseline && <span>Baseline: {item.baseline}</span>}
                                          {item.onset && (
                                            <span>{item.baseline ? " • " : ""}Onset: {item.onset}</span>
                                          )}
                                          <span>
                                            {(item.baseline || item.onset) ? " • " : ""}Status: {item.status}
                                          </span>
                                        </div>
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                <div className="space-y-3">
                                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                                    STEP 2: TIMELINE ANALYSIS
                                  </div>
                                  <ul className="space-y-2">
                                    {causalData.step2_timeline.map((item, index) => (
                                      <li
                                        key={`${item.week}-${index}`}
                                        className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-slate-200 bg-white p-3 text-sm"
                                      >
                                        <div className="font-medium text-slate-800">Week {item.week}</div>
                                        <div className="text-slate-700">{item.event}</div>
                                        <span
                                          className={`rounded-full border px-2 py-1 text-xs font-semibold ${getCausalSeverityClass(item.severity)}`}
                                        >
                                          {item.severity.toUpperCase()}
                                        </span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                <div className="space-y-3">
                                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                                    STEP 3: PHYSIOLOGICAL MECHANISMS & GRAPH
                                  </div>
                                  <ul className="space-y-2 text-sm text-slate-700">
                                    {causalData.step3_mechanisms.map((item, index) => (
                                      <li
                                        key={`${item.from}-${index}`}
                                        className="rounded-md border border-slate-200 bg-white p-3"
                                      >
                                        <span className="font-semibold">{item.from}</span> → {item.mechanism}
                                      </li>
                                    ))}
                                  </ul>
                                  <div className="mt-3 flex flex-col items-center gap-2">
                                    <div className="bg-white border-2 border-slate-400 px-4 py-2 rounded-md font-semibold">
                                      High BP (160/110)
                                    </div>
                                    <div className="text-slate-500 text-lg">↓</div>
                                    <div className="bg-white border-2 border-slate-400 px-4 py-2 rounded-md font-semibold">
                                      Vascular Damage
                                    </div>
                                    <div className="text-slate-500 text-lg">↓</div>
                                    <div className="bg-white border-2 border-slate-400 px-4 py-2 rounded-md font-semibold">
                                      Protein in Urine (2+)
                                    </div>
                                    <div className="text-slate-500 text-lg">↓</div>
                                    <div className="bg-white border-2 border-slate-400 px-4 py-2 rounded-md font-semibold">
                                      Kidney Stress
                                    </div>
                                    <div className="text-slate-500 text-lg">↓</div>
                                    <div className="bg-red-100 border-2 border-red-600 px-4 py-2 rounded-md font-semibold">
                                      Preeclampsia (85%)
                                    </div>
                                    <div className="text-slate-500 text-lg">↓</div>
                                    <div className="bg-red-100 border-2 border-red-600 px-4 py-2 rounded-md font-semibold">
                                      Transfer within 2h
                                    </div>
                                  </div>
                                </div>

                                <div className="space-y-3">
                                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                                    STEP 4: DIFFERENTIAL DIAGNOSIS
                                  </div>
                                  <ul className="space-y-2">
                                    {causalData.step4_diagnosis.map((item, index) => (
                                      <li
                                        key={`${item.condition}-${index}`}
                                        className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-slate-200 bg-white p-3 text-sm"
                                      >
                                        <div className="font-semibold text-slate-800">{item.condition}</div>
                                        <div className="text-slate-700">{item.probability}</div>
                                        <span
                                          className={`rounded-full border px-2 py-1 text-xs font-semibold ${getCausalSeverityClass(item.severity)}`}
                                        >
                                          {item.severity.toUpperCase()}
                                        </span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                <div className="space-y-3">
                                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-600">
                                    STEP 5: RECOMMENDATION
                                  </div>
                                  <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm">
                                    <div className="font-bold text-red-700">
                                      {causalData.step5_recommendation.action}
                                    </div>
                                    <div className="mt-2 text-slate-700">
                                      Timeframe: {causalData.step5_recommendation.timeframe}
                                    </div>
                                    <div className="text-slate-700">
                                      Facility: {causalData.step5_recommendation.facility}
                                    </div>
                                    <div className="text-slate-500 text-xs mt-1">
                                      WHO Reference: {causalData.step5_recommendation.who_reference}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </>
                        ) : null}
                      </CardContent>
                    </Card>
                  )}
                </CardContent>
              </Card>

              <div className="mb-4">
                <CheckupCountdown currentWeek={parseInt(weekOfPregnancy) || carePlan?.week_number || 20} />
              </div>

              {/* Emergency Access Card */}
              <Card className="border-destructive">
                <CardHeader>
                  <CardTitle className="text-destructive flex items-center gap-2">
                    <AlertCircle className="w-6 h-6" />
                    জরুরি সহায়তা / Emergency Access
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button onClick={handleEmergency} variant="destructive" size="lg" className="w-full h-16 text-lg">
                      <AlertCircle className="w-6 h-6 mr-2" />
                      জরুরি ড্যাশবোর্ড / Emergency Dashboard
                    </Button>
                  </motion.div>

                  <div className="grid grid-cols-2 gap-4">
                    <Button onClick={() => handleCall("999")} variant="outline" size="lg" className="h-14">
                      <Phone className="w-5 h-5 mr-2" />
                      999 অ্যাম্বুলেন্স
                    </Button>
                    <Button onClick={() => handleCall("16263")} variant="outline" size="lg" className="h-14">
                      <Phone className="w-5 h-5 mr-2" />
                      16263 স্বাস্থ্য
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Weekly Care Plan */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="w-6 h-6" />
                    সাপ্তাহিক যত্ন পরিকল্পনা / Weekly Care Plan
                  </CardTitle>
                  <CardDescription>সপ্তাহ {weekOfPregnancy || "20"} এর পরিকল্পনা / Week Care Plan</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Button onClick={handleGetCarePlan} disabled={loadingCarePlan} className="flex-1">
                      {loadingCarePlan ? "লোড হচ্ছে... / Loading..." : "এই সপ্তাহের পরিকল্পনা দেখুন / View This Week's Plan"}
                    </Button>
                    {carePlan && (
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={async () => {
                          try {
                            // Show some loading indicator if possible, or just play when ready
                            const checklistItems = carePlan.weekly_checklist
                              ? carePlan.weekly_checklist.map(i => i.title_bengali)
                              : [];

                            const res = await fetch(`${API_BASE_URL}/api/midwife/humanize-care-plan`, {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({
                                week_number: carePlan.week_number,
                                summary_text: `${carePlan.week_summary_bengali}. ${carePlan.baby_development_bengali}. ${carePlan.mother_changes_bengali}`,
                                checklist_items: checklistItems
                              })
                            });

                            if (res.ok) {
                              const data = await res.json();
                              playAudio(data.audio_text);
                            } else {
                              // Fallback if API fails
                              console.error("Humanize API failed, using fallback");
                              let text = `${carePlan.week_summary_bengali || ''}. ${carePlan.baby_development_bengali || ''}. ${carePlan.mother_changes_bengali || ''}.`;
                              if (carePlan.weekly_checklist && carePlan.weekly_checklist.length > 0) {
                                text += " আপনার করণীয়: ";
                                carePlan.weekly_checklist.forEach(item => {
                                  text += `${item.title_bengali}, `;
                                });
                              }
                              playAudio(text);
                            }
                          } catch (e) {
                            console.error("Error calling humanize API", e);
                            // Same fallback
                            let text = `${carePlan.week_summary_bengali || ''}. ${carePlan.baby_development_bengali || ''}. ${carePlan.mother_changes_bengali || ''}.`;
                            playAudio(text);
                          }
                        }}
                        title="শুনুন / Listen"
                      >
                        <Volume2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>

                  {carePlan && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">

                      <div>
                        <Label className="mb-2 block text-primary font-bold">চেকলিস্ট / Checklist</Label>
                        <div className="space-y-2">
                          {carePlan.weekly_checklist?.map((item, index) => (
                            <Card key={index} className={`bg-muted border-l-4 ${item.priority === 'high' ? 'border-l-destructive' : 'border-l-primary'}`}>
                              <CardContent className="pt-4 flex items-start gap-3">
                                {item.completed ? (
                                  <CheckCircle className="w-5 h-5 text-green-500 mt-1 shrink-0" />
                                ) : (
                                  <div className="w-5 h-5 border-2 border-muted-foreground rounded mt-1 shrink-0" />
                                )}
                                <div>
                                  <div className="flex items-center gap-2">
                                    <p className="font-medium">{item.title_bengali}</p>
                                    {item.priority === 'high' && <Badge variant="destructive" className="text-[10px] py-0">Urgent</Badge>}
                                  </div>
                                  <p className="text-xs text-muted-foreground">{item.description_bengali}</p>
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label className="mb-2 block font-bold">পুষ্টি লক্ষ্য / Nutrition Focus</Label>
                          <Card className="bg-primary/10 border-primary/20">
                            <CardContent className="pt-4">
                              <p className="text-sm font-medium">{carePlan.nutrition_focus?.join(" • ")}</p>
                              {carePlan.foods_to_emphasize?.length > 0 && (
                                <p className="text-xs mt-2 text-muted-foreground">পছন্দ করুন: {carePlan.foods_to_emphasize.join(", ")}</p>
                              )}
                            </CardContent>
                          </Card>
                        </div>

                        <div>
                          <Label className="mb-2 block font-bold">সতর্কতা লক্ষণ / Warning Signs</Label>
                          <div className="space-y-2">
                            {carePlan.warning_signs?.slice(0, 3).map((sign, index) => (
                              <Card key={index} className="bg-destructive/5 border-destructive/10">
                                <CardContent className="py-2 px-3 flex items-center gap-2">
                                  <AlertTriangle className={`w-4 h-4 ${sign.is_emergency ? 'text-destructive' : 'text-orange-500'}`} />
                                  <p className="text-[13px]">{sign.sign_bengali}</p>
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </CardContent>
              </Card>

              {/* Profile Setup */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="w-6 h-6" />
                    প্রোফাইল সেটআপ / Profile Setup
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="age">বয়স / Age</Label>
                      <Input
                        id="age"
                        type="number"
                        placeholder="25"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="week">গর্ভাবস্থার সপ্তাহ / Week</Label>
                      <Input
                        id="week"
                        type="number"
                        placeholder="20"
                        value={weekOfPregnancy}
                        onChange={(e) => setWeekOfPregnancy(e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="weight">ওজন (kg) / Weight</Label>
                      <Input
                        id="weight"
                        type="number"
                        placeholder="60"
                        value={weight}
                        onChange={(e) => setWeight(e.target.value)}
                      />
                    </div>
                    <div>
                      <Label htmlFor="gravida">গ্রাভিডা / Gravida</Label>
                      <Select value={gravida} onValueChange={setGravida}>
                        <SelectTrigger id="gravida">
                          <SelectValue placeholder="নির্বাচন করুন" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="first">প্রথম শিশু / 1st baby</SelectItem>
                          <SelectItem value="second">দ্বিতীয় শিশু / 2nd baby</SelectItem>
                          <SelectItem value="third">তৃতীয় শিশু / 3rd baby</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Button onClick={handleSaveProfile} className="w-full">
                    প্রোফাইল সংরক্ষণ করুন / Save Profile
                  </Button>

                  <div className="relative flex py-2 items-center">
                    <div className="flex-grow border-t border-muted"></div>
                    <span className="flex-shrink-0 mx-4 text-muted-foreground text-xs">Medical Tools</span>
                    <div className="flex-grow border-t border-muted"></div>
                  </div>

                  <Button
                    onClick={handleGenerateClinicalReport}
                    disabled={loadingReport}
                    variant="outline"
                    className="w-full border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100"
                  >
                    {loadingReport ? (
                      "তৈরি হচ্ছে... / Generatng..."
                    ) : (
                      <>
                        <Stethoscope className="w-4 h-4 mr-2" />
                        ডাক্তারের জন্য রিপোর্ট তৈরি করুন / Generate Clinical Report
                      </>
                    )}
                  </Button>

                  {clinicalReport && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                      <Card className="bg-white border-blue-200 shadow-sm">
                        <CardHeader className="pb-2 bg-blue-50/50">
                          <CardTitle className="text-base text-blue-900 flex items-center gap-2">
                            <FileText className="w-4 h-4" />
                            Clinical Insight Report
                          </CardTitle>
                          <CardDescription className="text-xs">
                            Confid: {(clinicalReport.confidence_score * 100).toFixed(0)}%
                          </CardDescription>
                        </CardHeader>
                        <CardContent className="pt-4 text-sm space-y-3">
                          <div>
                            <p className="font-semibold text-gray-700 text-xs uppercase">Summary</p>
                            <p className="text-gray-900">{clinicalReport.clinical_summary}</p>
                          </div>

                          {clinicalReport.differential_diagnoses?.length > 0 && (
                            <div>
                              <p className="font-semibold text-gray-700 text-xs uppercase mb-1">Differential Diagnosis</p>
                              <div className="space-y-2">
                                {clinicalReport.differential_diagnoses.map((dx: any, i: number) => (
                                  <div key={i} className="bg-slate-50 p-2 rounded border border-slate-100">
                                    <div className="flex justify-between">
                                      <span className="font-medium">{dx.condition_name}</span>
                                      <Badge variant={dx.likelihood === 'High' ? 'destructive' : 'outline'} className="text-[10px] h-5">
                                        {dx.likelihood}
                                      </Badge>
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-1">{dx.supporting_evidence?.join(", ")}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          <div>
                            <p className="font-semibold text-gray-700 text-xs uppercase">Action Plan</p>
                            <ul className="list-disc list-inside text-gray-800">
                              {clinicalReport.recommended_interventions?.map((action: any, i: number) => (
                                <li key={i}>{action.action} ({action.urgency})</li>
                              ))}
                            </ul>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {activeTab === "nutrition" && (
            <motion.div
              key="nutrition"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {/* Personalized Menu Generator */}
              <Card>
                <CardHeader>
                  <CardTitle>ব্যক্তিগত মেনু তৈরি / Personalized Menu Generator</CardTitle>
                  <CardDescription>৭ দিনের খাদ্য পরিকল্পনা পান / Get your 7-day menu</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="trimester">ত্রৈমাসিক / Trimester</Label>
                    <Select value={trimester} onValueChange={setTrimester}>
                      <SelectTrigger id="trimester">
                        <SelectValue placeholder="নির্বাচন করুন / Select trimester" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="first">প্রথম / First Trimester</SelectItem>
                        <SelectItem value="second">দ্বিতীয় / Second Trimester</SelectItem>
                        <SelectItem value="third">তৃতীয় / Third Trimester</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="budget">সাপ্তাহিক বাজেট (BDT) / Weekly Budget</Label>
                    <Input
                      id="budget"
                      type="number"
                      placeholder="যেমন: 1500 / e.g., 1500"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                    />
                  </div>

                  <div>
                    <Label>স্বাস্থ্য অবস্থা / Health Conditions</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {["Anemia", "Diabetes", "Hypertension"].map((condition) => (
                        <Badge
                          key={condition}
                          variant={conditions.includes(condition.toLowerCase()) ? "default" : "outline"}
                          className="cursor-pointer"
                          onClick={() => handleConditionToggle(condition.toLowerCase())}
                        >
                          {condition === "Anemia"
                            ? "রক্তশূন্যতা / Anemia"
                            : condition === "Diabetes"
                              ? "ডায়াবেটিস / Diabetes"
                              : "উচ্চ রক্তচাপ / Hypertension"}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <Button onClick={handleGetFoodPlan} disabled={loadingFood} className="w-full">
                    {loadingFood ? "তৈরি হচ্ছে... / Generating..." : "৭ দিনের মেনু তৈরি করুন / Generate 7-Day Menu"}
                  </Button>
                </CardContent>
              </Card>

              {/* Food List Results - Grid Display */}
              {foodItems.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>আপনার ৭ দিনের খাদ্য তালিকা / Your 7-Day Food List</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {foodItems.map((item, index) => (
                        <motion.div
                          key={index}
                          className="bg-card text-card-foreground rounded-xl border shadow-sm overflow-hidden hover:shadow-lg transition-all cursor-pointer group"
                          onClick={() => setSelectedFoodItem(item)}
                          whileHover={{ y: -4 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <div className="relative">
                            {item.image_url ? (
                              <img
                                src={item.image_url.startsWith('http') ? item.image_url : `http://localhost:8000${item.image_url}`}
                                alt={item.name_bengali}
                                className="w-full h-40 object-cover"
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement;
                                  target.onerror = null;
                                  target.src = "https://placehold.co/600x400/e0e0e0/333333?text=No+Image";
                                }}
                              />
                            ) : (
                              <div className="w-full h-40 bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                                <Utensils className="w-12 h-12 text-muted-foreground" />
                              </div>
                            )}
                            {/* Price Badge - Top Left */}
                            <Badge className="absolute top-2 left-2 bg-primary text-primary-foreground px-3 py-1 text-sm font-semibold shadow-md">
                              ৳{item.price_bdt}
                            </Badge>
                            {/* AI Generated Badge */}
                            {item.image_url && (
                              <Badge className="absolute top-2 right-2 bg-secondary text-secondary-foreground px-2 py-1 text-xs">
                                AI Generated
                              </Badge>
                            )}
                          </div>
                          <div className="p-4 space-y-2">
                            {/* Food Names */}
                            <div>
                              <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors">{item.name_bengali}</h3>
                              <p className="text-sm text-muted-foreground">{item.name_english}</p>
                            </div>
                            {/* Nutrition Info */}
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <span className="font-medium">{item.calories}</span> kcal
                              </span>
                              <span className="text-muted-foreground">|</span>
                              <span className="flex items-center gap-1">
                                <span className="font-medium">{item.protein_g}g</span> Protein
                              </span>
                            </div>
                            {/* Benefits */}
                            <div className="flex justify-between items-center mt-2">
                              <Badge variant="secondary">
                                {item.benefits_key}
                              </Badge>
                              <div className="flex gap-2">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 rounded-full"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handlePlayAudioScript(item.audio_script_bengali || item.name_bengali);
                                  }}
                                >
                                  <Volume2 className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="text-xs h-8"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedFoodItem(item);
                                  }}
                                >
                                  রেসিপি / Recipe
                                </Button>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>

                    <div className="flex flex-col gap-3 pt-4">
                      {currentPhase < 3 && (
                        <Button
                          onClick={handleLoadMoreItems}
                          disabled={loadingFood}
                          variant="outline"
                          className="w-full h-12"
                        >
                          {loadingFood ? "লোড হচ্ছে... / Loading..." : "আরো কিছু ট্রাই করুন / Try Something Different"}
                        </Button>
                      )}

                      <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                        <Button onClick={handleStartShopping} className="w-full h-14 text-lg" size="lg">
                          <ShoppingBag className="w-6 h-6 mr-2" />🛒 বাজার খুঁজুন / Find Markets
                        </Button>
                      </motion.div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Quick Food Safety Check */}
              <Card>
                <CardHeader>
                  <CardTitle>দ্রুত খাদ্য নিরাপত্তা পরীক্ষা / Quick Food Safety Check</CardTitle>
                  <CardDescription>আমি কি এটি খেতে পারি? / Can I eat this?</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="foodCheck">খাবারের নাম লিখুন / Enter food name</Label>
                    <div className="flex gap-2">
                      <Input
                        id="foodCheck"
                        placeholder="যেমন: আনারস / e.g., Pineapple"
                        value={foodCheckInput}
                        onChange={(e) => setFoodCheckInput(e.target.value)}
                      />
                      <Button onClick={handleFoodSafetyCheck} disabled={loadingFoodCheck}>
                        {loadingFoodCheck ? "পরীক্ষা..." : "পরীক্ষা / Check"}
                      </Button>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="flex-1 border-t border-border" />
                    <span className="text-sm text-muted-foreground">অথবা / OR</span>
                    <div className="flex-1 border-t border-border" />
                  </div>

                  <div>
                    <Label>ছবি আপলোড করুন / Upload Image</Label>
                    <div className="mt-2">
                      <label htmlFor="foodImage" className="cursor-pointer">
                        <div className="border-2 border-dashed border-border rounded-lg p-6 flex flex-col items-center gap-2 hover:bg-muted transition-colors">
                          <Camera className="w-8 h-8 text-muted-foreground" />
                          <p className="text-sm text-muted-foreground">খাবারের ছবি তুলুন / Take photo of food</p>
                        </div>
                        <Input
                          id="foodImage"
                          type="file"
                          accept="image/*"
                          capture="environment"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0]
                            if (file) handleFoodImageCheck(file)
                          }}
                        />
                      </label>
                    </div>
                  </div>

                  {foodSafetyResult && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                      <Card className={
                        foodSafetyResult.safe ? (foodSafetyResult.is_caution ? "border-yellow-500 bg-yellow-50/10" : "border-green-500") : "border-red-500"
                      }>
                        <CardContent className="pt-6 space-y-4">
                          <div className="flex items-center gap-3">
                            {foodSafetyResult.safe ? (
                              foodSafetyResult.is_caution ? (
                                <AlertTriangle className="w-8 h-8 text-yellow-500" />
                              ) : (
                                <CheckCircle className="w-8 h-8 text-green-500" />
                              )
                            ) : (
                              <XCircle className="w-8 h-8 text-red-500" />
                            )}
                            <div>
                              <p className="font-semibold text-lg">
                                {foodSafetyResult.safe ?
                                  (foodSafetyResult.is_caution ? "সতর্কতা / Caution" : "নিরাপদ খাবার / Safe to Eat")
                                  : "এড়িয়ে চলুন / Avoid This Food"}
                              </p>
                              <p className="text-sm text-muted-foreground">{foodSafetyResult.reason_bengali}</p>
                            </div>
                          </div>

                          {!foodSafetyResult.safe && foodSafetyResult.alternatives_bengali && (
                            <div>
                              <Label className="mb-2 block">বিকল্প / Alternatives</Label>
                              <ul className="list-disc list-inside space-y-1 text-sm">
                                {foodSafetyResult.alternatives_bengali.map((alt, index) => (
                                  <li key={index}>{alt}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}
                </CardContent>
              </Card>

              {/* Medical Document Upload */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="w-6 h-6" />
                    চিকিৎসা নথি আপলোড / Medical Document Upload
                  </CardTitle>
                  <CardDescription>প্রেসক্রিপশন আপলোড করুন / Upload prescription</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label htmlFor="docUpload" className="cursor-pointer">
                      <div className="border-2 border-dashed border-border rounded-lg p-8 flex flex-col items-center gap-3 hover:bg-muted transition-colors">
                        <Upload className="w-10 h-10 text-muted-foreground" />
                        <div className="text-center">
                          <p className="font-medium">প্রেসক্রিপশন আপলোড করুন / Upload Prescription</p>
                          <p className="text-sm text-muted-foreground">.doc, .docx ফাইল / .doc, .docx files</p>
                        </div>
                        {uploadedFile && (
                          <Badge variant="secondary" className="mt-2">
                            {uploadedFile.name}
                          </Badge>
                        )}
                      </div>
                      <Input
                        id="docUpload"
                        type="file"
                        accept=".doc,.docx"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files?.[0]
                          if (file) handleDocumentUpload(file)
                        }}
                      />
                    </label>
                  </div>

                  {uploadingDoc && <p className="text-center text-muted-foreground">আপলোড হচ্ছে... / Uploading...</p>}

                  {uploadedFile && (
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                      <Card className="bg-green-50 border-green-200">
                        <CardContent className="pt-6 flex items-center gap-3">
                          <CheckCircle className="w-6 h-6 text-green-500 shrink-0" />
                          <div>
                            <p className="font-medium">নথি সফলভাবে আপলোড করা হয়েছে / Document uploaded</p>
                            <p className="text-sm text-muted-foreground">
                              প্রোফাইল স্বয়ংক্রিয়ভাবে আপডেট করা হয়েছে / Profile auto-filled
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Recipe Modal */}
        <AnimatePresence>
          {selectedFoodItem && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
              onClick={() => setSelectedFoodItem(null)}
            >
              <motion.div
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
                className="bg-card w-full max-w-lg rounded-2xl overflow-hidden shadow-2xl border border-border"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="relative h-48 bg-muted">
                  {selectedFoodItem.image_url ? (
                    <img
                      src={selectedFoodItem.image_url.startsWith('http') ? selectedFoodItem.image_url : `http://localhost:8000${selectedFoodItem.image_url}`}
                      alt={selectedFoodItem.name_bengali}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.onerror = null;
                        target.src = "https://placehold.co/600x400/e0e0e0/333333?text=No+Image";
                      }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/10 to-secondary/10">
                      <Utensils className="w-16 h-16 text-muted-foreground/30" />
                    </div>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute top-2 right-2 rounded-full bg-black/20 hover:bg-black/40 text-white"
                    onClick={() => setSelectedFoodItem(null)}
                  >
                    <XCircle className="h-6 w-6" />
                  </Button>
                </div>
                <div className="p-6 space-y-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h2 className="text-2xl font-bold">{selectedFoodItem.name_bengali}</h2>
                      <p className="text-muted-foreground">{selectedFoodItem.name_english}</p>
                    </div>
                    <Button
                      variant="default"
                      onClick={() => handlePlayAudioScript(selectedFoodItem.audio_script_bengali || selectedFoodItem.recipe_bengali || "")}
                      className="rounded-full h-12 w-12 p-0"
                    >
                      <Volume2 className="h-6 w-6" />
                    </Button>
                  </div>

                  <div className="bg-muted/30 p-4 rounded-xl">
                    <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-2">উপকারিতা / Benefits</h3>
                    <p className="font-medium text-primary">{selectedFoodItem.benefits_key}</p>
                    <div className="flex gap-4 mt-2 text-sm">
                      <span>🔥 {selectedFoodItem.calories} kcal</span>
                      <span>💪 {selectedFoodItem.protein_g}g প্রোটিন</span>
                    </div>
                  </div>

                  <div className="max-h-60 overflow-y-auto pr-2 space-y-2">
                    <h3 className="text-lg font-bold">রান্নার নিয়ম / Recipe</h3>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">
                      {selectedFoodItem.recipe_bengali || "রেসিপি পাওয়া যায়নি।"}
                    </p>
                  </div>

                  <Button onClick={() => setSelectedFoodItem(null)} className="w-full mt-4">বন্ধ করুন / Close</Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-card border-t border-border shadow-lg">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="grid grid-cols-2 gap-2 py-3">
            <Button
              variant={activeTab === "home" ? "default" : "ghost"}
              onClick={() => setActiveTab("home")}
              className="flex flex-col h-auto py-3 gap-1"
            >
              <Home className="w-5 h-5" />
              <span className="text-xs">হোম / Home</span>
            </Button>
            <Button
              variant={activeTab === "nutrition" ? "default" : "ghost"}
              onClick={() => setActiveTab("nutrition")}
              className="flex flex-col h-auto py-3 gap-1"
            >
              <Utensils className="w-5 h-5" />
              <span className="text-xs">খাদ্য / Food</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
