"use client"

import React, { createContext, useContext, useState, useEffect } from "react"

const API_BASE_URL = ""

interface User {
    id: string
    name: string
    phone: string
}

interface AuthContextType {
    user: User | null
    token: string | null
    login: (phone: string, pin: string) => Promise<void>
    register: (phone: string, pin: string, name: string) => Promise<void>
    logout: () => void
    isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        // Load from local storage on mount
        const storedToken = localStorage.getItem("janani_token")
        if (storedToken) {
            verifyToken(storedToken)
        } else {
            setIsLoading(false)
        }
    }, [])

    const verifyToken = async (storedToken: string) => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/auth/me?token=${storedToken}`)
            if (res.ok) {
                const userData = await res.json()
                setUser(userData)
                setToken(storedToken)
            } else {
                logout()
            }
        } catch (e) {
            console.error("Token verification failed", e)
            // Offline support: If network fails, we might still want to trust the token or show offline mode
            // For now, simple fail
            logout()
        } finally {
            setIsLoading(false)
        }
    }

    const login = async (phone: string, pin: string) => {
        setIsLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone, pin }),
            })

            if (!res.ok) {
                const err = await res.json()
                throw new Error(err.detail || "Login failed")
            }

            const data = await res.json()
            // data = { access_token, user_id, name, ... }

            setToken(data.access_token)
            setUser({ id: data.user_id, name: data.name, phone: phone })
            localStorage.setItem("janani_token", data.access_token)

        } catch (error) {
            console.error(error)
            throw error
        } finally {
            setIsLoading(false)
        }
    }

    const register = async (phone: string, pin: string, name: string) => {
        setIsLoading(true)
        try {
            const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone, pin, name }),
            })

            if (!res.ok) {
                const err = await res.json()
                throw new Error(err.detail || "Registration failed")
            }

            const data = await res.json()

            setToken(data.access_token)
            setUser({ id: data.user_id, name: data.name, phone: phone })
            localStorage.setItem("janani_token", data.access_token)

        } catch (error) {
            console.error(error)
            throw error
        } finally {
            setIsLoading(false)
        }
    }

    const logout = () => {
        setUser(null)
        setToken(null)
        localStorage.removeItem("janani_token")
    }

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider")
    }
    return context
}
