"use client"

import { useState } from "react"
import { Calendar, Clock, CheckCircle, Circle, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface CheckupCountdownProps {
    currentWeek: number
}

// WHO Recommended 8 Contacts Schedule
const ANC_SCHEDULE = [
    { week: 12, label: "১ম ভিজিট (First Contact)", focus: "Pregnancy confirmation, dating, screening" },
    { week: 20, label: "২য় ভিজিট (Second Contact)", focus: "Anomaly scan, movement check" },
    { week: 26, label: "৩য় ভিজিট (Third Contact)", focus: "Diabetes test (OGTT), anemia check" },
    { week: 30, label: "৪র্থ ভিজিট (Fourth Contact)", focus: "Growth scan, BP check" },
    { week: 34, label: "৫ম ভিজিট (Fifth Contact)", focus: "Birth planning, position check" },
    { week: 36, label: "৬ষ্ঠ ভিজিট (Sixth Contact)", focus: "Final checks, GBS test" },
    { week: 38, label: "৭ম ভিজিট (Seventh Contact)", focus: "Pre-labor check" },
    { week: 40, label: "৮ম ভিজিট (Eighth Contact)", focus: "Delivery discussion" },
]

export function CheckupCountdown({ currentWeek }: CheckupCountdownProps) {
    const [open, setOpen] = useState(false)

    // Find next visit
    const nextVisit = ANC_SCHEDULE.find((v) => v.week >= currentWeek) || ANC_SCHEDULE[ANC_SCHEDULE.length - 1]
    const isCompleted = currentWeek > 40

    // Calculate approximate days
    const weeksRemaining = nextVisit.week - currentWeek
    const daysRemaining = Math.max(0, weeksRemaining * 7)

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button
                    variant="outline"
                    className="w-full flex justify-between items-center bg-teal-50 hover:bg-teal-100 border-teal-200 text-teal-900 group"
                >
                    <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-teal-600" />
                        <span className="font-semibold">
                            {isCompleted ? "চেকআপ সম্পন্ন" : `পরবর্তী চেকআপ: ${daysRemaining} দিন বাকি`}
                        </span>
                    </div>
                    <Badge variant="secondary" className="bg-white text-teal-700 hover:bg-white/80">
                        সপ্তাহ {nextVisit.week}
                    </Badge>
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
                <DialogHeader>
                    <DialogTitle className="text-xl font-bold flex items-center gap-2">
                        <Calendar className="w-5 h-5 text-teal-600" />
                        ANC চেকআপ রুটিন
                    </DialogTitle>
                    <DialogDescription>
                        বিশ্ব স্বাস্থ্য সংস্থার (WHO) পরামর্শ অনুযায়ী আপনার চেকআপ শিডিউল
                    </DialogDescription>
                </DialogHeader>

                <ScrollArea className="h-[60vh] pr-4">
                    <div className="space-y-4 py-2">
                        {ANC_SCHEDULE.map((visit, index) => {
                            const visitStatus =
                                currentWeek > visit.week + 1 ? "completed" :
                                    currentWeek >= visit.week - 1 ? "current" : "future"

                            return (
                                <Card
                                    key={index}
                                    className={`border-l-4 transition-all ${visitStatus === "completed" ? "border-l-green-500 bg-green-50/50 opacity-70" :
                                            visitStatus === "current" ? "border-l-teal-500 bg-white shadow-md ring-1 ring-teal-200" :
                                                "border-l-gray-300 bg-gray-50 text-gray-500"
                                        }`}
                                >
                                    <CardContent className="p-4 flex items-start gap-3">
                                        <div className="mt-1">
                                            {visitStatus === "completed" ? (
                                                <CheckCircle className="w-5 h-5 text-green-600" />
                                            ) : visitStatus === "current" ? (
                                                <div className="relative">
                                                    <div className="absolute -inset-1 rounded-full bg-teal-200 animate-ping opacity-75" />
                                                    <Circle className="w-5 h-5 text-teal-600 fill-teal-100" />
                                                </div>
                                            ) : (
                                                <Circle className="w-5 h-5 text-gray-300" />
                                            )}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex justify-between items-center mb-1">
                                                <h4 className={`font-bold ${visitStatus === "current" ? "text-teal-900" : "text-gray-900"}`}>
                                                    {visit.label}
                                                </h4>
                                                <Badge variant={visitStatus === "current" ? "default" : "outline"}>
                                                    সপ্তাহ {visit.week}
                                                </Badge>
                                            </div>
                                            <p className="text-sm text-gray-600 mb-2">{visit.focus}</p>

                                            {visitStatus === "current" && (
                                                <div className="bg-teal-100/50 p-2 rounded text-xs text-teal-800 font-medium flex items-center gap-1">
                                                    <ArrowRight className="w-3 h-3" />
                                                    এখনই অ্যাপয়েন্টমেন্ট নিন
                                                </div>
                                            )}
                                        </div>
                                    </CardContent>
                                </Card>
                            )
                        })}
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    )
}
