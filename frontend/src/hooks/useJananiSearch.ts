import { useEffect, useState, useRef } from 'react';
import { db } from '../db/janani.db'; // Ensure this path is correct

export function useJananiSearch() {
    const [searchMode, setSearchMode] = useState<'BASIC' | 'AI'>('BASIC');
    const [results, setResults] = useState<any[]>([]);
    const workerRef = useRef<Worker | null>(null);

    useEffect(() => {
        // 1. Initialize Worker
        workerRef.current = new Worker(new URL('../workers/search.worker.ts', import.meta.url), {
            type: 'module'
        });

        // 2. Handle Messages from Worker
        workerRef.current.onmessage = async (e) => {
            const { type, payload, mode } = e.data;

            // A. Catch the Vectors and Save to DB
            if (type === 'VECTORS_GENERATED') {
                console.log(`💾 Main Thread: Saving ${payload.length} vectors to Dexie...`);
                try {
                    await db.vectors.clear(); // Clear old math to be safe
                    await db.vectors.bulkPut(payload);
                    console.log("✅ Success: Long-term memory updated!");
                } catch (err) {
                    console.error("❌ Failed to save vectors:", err);
                }
            }

            // B. Update Status Badge
            if (type === 'STATUS') {
                setSearchMode(mode === 'AI_READY' ? 'AI' : 'BASIC');
            }

            // C. Handle Search Results
            if (type === 'RESULTS') {
                setResults(payload);
            }
        };

        // 3. Kickstart the Process - CHECK INDEXEDDB FIRST
        async function initializeWorker() {
            try {
                // Check if vectors already exist in IndexedDB
                const existingVectorCount = await db.vectors.count();

                if (existingVectorCount > 0) {
                    // ✅ Vectors exist! Load from IndexedDB and send to worker
                    console.log(`📦 Main Thread: Found ${existingVectorCount} vectors in IndexedDB, loading to worker...`);
                    const existingVectors = await db.vectors.toArray();

                    // Also fetch guidelines to attach the 'item' data
                    const guidelines = await db.guidelines.toArray();
                    const guidelinesMap = new Map(guidelines.map(g => [g.id, g]));

                    // Reconstruct the full payload with item data
                    const vectorsWithItems = existingVectors.map(v => ({
                        guidelineId: v.guidelineId,
                        vector: v.vector,
                        item: guidelinesMap.get(v.guidelineId) || null
                    }));

                    workerRef.current?.postMessage({
                        type: 'LOAD_VECTORS',
                        payload: { vectors: vectorsWithItems }
                    });
                } else {
                    // ❌ No vectors, need to generate them
                    console.log("🆕 Main Thread: No vectors in IndexedDB, generating...");
                    const response = await fetch('/data/who_guidelines.json');
                    const data = await response.json();

                    workerRef.current?.postMessage({
                        type: 'INIT',
                        payload: { guidelines: data }
                    });
                }
            } catch (err) {
                console.error("❌ Main Thread: Initialization error:", err);
                // Fallback: try to generate vectors anyway
                const response = await fetch('/data/who_guidelines.json');
                const data = await response.json();
                workerRef.current?.postMessage({
                    type: 'INIT',
                    payload: { guidelines: data }
                });
            }
        }

        initializeWorker();

        return () => workerRef.current?.terminate();
    }, []);

    // Search function
    return {
        searchMode,
        results,
        search: (query: string) => workerRef.current?.postMessage({ type: 'SEARCH', payload: { query } })
    };
}
