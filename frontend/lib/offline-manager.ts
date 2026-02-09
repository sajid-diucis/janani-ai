
"use client"

import { useEffect, useState } from "react"

export interface OfflineRule {
    keywords: string[]
    response_bengali: string
    risk_level: string
    action?: string
}

export interface OfflineData {
    rules: OfflineRule[]
    emergency_contacts: {
        ambulance: string
        health_line: string
    }
}

class OfflineManager {
    private rules: OfflineRule[] = []

    constructor() {
        if (typeof window !== "undefined") {
            this.loadRules()
            this.setupSyncListener()
        }
    }

    private async loadRules() {
        try {
            // Try to fetch from public folder (cached by SW)
            const res = await fetch("/offline_rules.json")
            if (res.ok) {
                const data = await res.json()
                this.rules = data.rules
                localStorage.setItem("janani_offline_rules", JSON.stringify(data))
            }
        } catch (e) {
            // If fetch fails (offline & not cached), load from localStorage
            const cached = localStorage.getItem("janani_offline_rules")
            if (cached) {
                const data = JSON.parse(cached)
                this.rules = data.rules
            }
        }
    }

    public getOfflineResponse(query: string): string | null {
        if (!this.rules.length) return null;

        const lowerQuery = query.toLowerCase()
        for (const rule of this.rules) {
            if (rule.keywords.some(k => lowerQuery.includes(k.toLowerCase()))) {
                return rule.response_bengali
            }
        }
        return null
    }

    // --- Sync Logic ---

    public queueSyncItem(url: string, method: string, body: any) {
        const queue = JSON.parse(localStorage.getItem("janani_sync_queue") || "[]")
        queue.push({
            url,
            method,
            body,
            timestamp: Date.now()
        })
        localStorage.setItem("janani_sync_queue", JSON.stringify(queue))
    }

    private setupSyncListener() {
        window.addEventListener("online", () => {
            console.log("Network restored. Syncing data...")
            this.processQueue()
        })
    }

    private async processQueue() {
        const queue = JSON.parse(localStorage.getItem("janani_sync_queue") || "[]")
        if (queue.length === 0) return

        const remainingQueue = []

        for (const item of queue) {
            try {
                // If it's internal API, prepend base URL if needed, 
                // but usually we store relative or full. 
                // Assuming relative for internal API usually works if on same domain, 
                // but safely let's use the stored URL.
                await fetch(item.url, {
                    method: item.method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(item.body)
                })
            } catch (e) {
                console.error("Sync failed for item", item, e)
                remainingQueue.push(item) // Keep in queue if still failing
            }
        }

        localStorage.setItem("janani_sync_queue", JSON.stringify(remainingQueue))
        if (remainingQueue.length === 0) {
            console.log("All offline data synced!")
        }
    }
}

export const offlineManager = new OfflineManager()
