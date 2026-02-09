"use client"

import { useState } from "react"
import { useAuth } from "@/context/auth-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2 } from "lucide-react"

export function LoginPage() {
    const { login, register, isLoading } = useAuth()
    const [error, setError] = useState("")

    // Form State
    const [phone, setPhone] = useState("")
    const [pin, setPin] = useState("")
    const [name, setName] = useState("")

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setError("")
        if (!phone || !pin) {
            setError("Please fill all fields")
            return
        }
        try {
            await login(phone, pin)
        } catch (err: any) {
            setError(err.message || "Failed to login")
        }
    }

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        setError("")
        if (!phone || !pin || !name) {
            setError("Please fill all fields")
            return
        }
        try {
            await register(phone, pin, name)
        } catch (err: any) {
            setError(err.message || "Failed to register")
        }
    }

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold text-teal-700">জননী (Janani)</CardTitle>
                    <CardDescription>ডিজিটাল মিডওয়াইফ - আপনার গর্ভাবস্থার সঙ্গী</CardDescription>
                </CardHeader>
                <CardContent>
                    <Tabs defaultValue="login" className="w-full">
                        <TabsList className="grid w-full grid-cols-2 mb-4">
                            <TabsTrigger value="login">লগইন (Login)</TabsTrigger>
                            <TabsTrigger value="register">নিবন্ধন (Register)</TabsTrigger>
                        </TabsList>

                        <TabsContent value="login">
                            <form onSubmit={handleLogin} className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="phone">মোবাইল নম্বর (Phone)</Label>
                                    <Input
                                        id="phone"
                                        placeholder="017xxxxxxxx"
                                        value={phone}
                                        onChange={(e) => setPhone(e.target.value)}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="pin">গোপন পিন (PIN)</Label>
                                    <Input
                                        id="pin"
                                        type="password"
                                        placeholder="****"
                                        value={pin}
                                        onChange={(e) => setPin(e.target.value)}
                                    />
                                </div>
                                {error && <p className="text-sm text-red-500 font-medium">{error}</p>}

                                <Button type="submit" className="w-full bg-teal-600 hover:bg-teal-700" disabled={isLoading}>
                                    {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "লগইন করুন"}
                                </Button>
                            </form>
                        </TabsContent>

                        <TabsContent value="register">
                            <form onSubmit={handleRegister} className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="reg-name">আপনার নাম (Name)</Label>
                                    <Input
                                        id="reg-name"
                                        placeholder="আপনার নাম লিখুন"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="reg-phone">মোবাইল নম্বর (Phone)</Label>
                                    <Input
                                        id="reg-phone"
                                        placeholder="017xxxxxxxx"
                                        value={phone}
                                        onChange={(e) => setPhone(e.target.value)}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="reg-pin">গোপন পিন (PIN)</Label>
                                    <Input
                                        id="reg-pin"
                                        type="password"
                                        placeholder="****"
                                        value={pin}
                                        onChange={(e) => setPin(e.target.value)}
                                    />
                                </div>
                                {error && <p className="text-sm text-red-500 font-medium">{error}</p>}

                                <Button type="submit" className="w-full bg-teal-600 hover:bg-teal-700" disabled={isLoading}>
                                    {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "অ্যাকাউন্ট তৈরি করুন"}
                                </Button>
                            </form>
                        </TabsContent>
                    </Tabs>
                </CardContent>
            </Card>
        </div>
    )
}
