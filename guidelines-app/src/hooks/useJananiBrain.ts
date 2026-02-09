'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { db, seedDatabase, type Guideline, type GuidelineVector } from '../db/janani.db';

export interface SearchResult extends Guideline {
    score: number;
}

export interface JananiBrainState {
    isReady: boolean;
    isLoading: boolean;
    isSearching: boolean;
    modelStatus: string;
    searchMode: 'AI_READY' | 'BASIC_MODE' | 'INITIALIZING';
    error: string | null;
}

export function useJananiBrain() {
    const [state, setState] = useState<JananiBrainState>({
        isReady: false,
        isLoading: true,
        isSearching: false,
        modelStatus: 'শুরু হচ্ছে...',
        searchMode: 'INITIALIZING',
        error: null
    });

    const workerRef = useRef<Worker | null>(null);

    // Initialize Worker & Database
    useEffect(() => {
        const init = async () => {
            try {
                setState(prev => ({ ...prev, modelStatus: 'ডাটাবেস লোড হচ্ছে...' }));
                await seedDatabase();

                // Initialize Worker
                setState(prev => ({ ...prev, modelStatus: 'AI মডেল লোড হচ্ছে (অপেক্ষা করুন)...' }));

                workerRef.current = new Worker(new URL('../workers/search.worker.ts', import.meta.url));

                workerRef.current.onmessage = (event) => {
                    const { type, mode, results, error } = event.data;

                    if (type === 'STATUS') {
                        if (mode === 'AI_READY') {
                            console.log('[JananiBrain] AI Ready (God Tier)');
                            setState(prev => ({
                                ...prev,
                                isReady: true,
                                isLoading: false,
                                searchMode: 'AI_READY',
                                modelStatus: '🟢 AI সার্চ (God Tier)',
                                error: null
                            }));
                        } else if (mode === 'BASIC_MODE') {
                            console.log('[JananiBrain] Fallback to Basic Mode (Toy Tier)');
                            setState(prev => ({
                                ...prev,
                                isReady: true,
                                isLoading: false,
                                searchMode: 'BASIC_MODE',
                                modelStatus: '🟠 সাধারণ সার্চ (Toy Tier)',
                                error: error || 'AI Load Failed'
                            }));
                        }
                    }
                };

                // Start initialization in worker
                workerRef.current.postMessage({ type: 'INIT' });

            } catch (err) {
                console.error('[JananiBrain] Init failed:', err);
                setState(prev => ({
                    ...prev,
                    isLoading: false,
                    isReady: true, // Still usable via DB fallback logic
                    searchMode: 'BASIC_MODE',
                    modelStatus: '🔴 এরর (সাধারণ মোড)',
                    error: err instanceof Error ? err.message : 'Unknown error'
                }));
            }
        };

        init();

        return () => {
            workerRef.current?.terminate();
        };
    }, []);

    // Hybrid Search Function
    const search = useCallback(async (query: string, topK: number = 5): Promise<SearchResult[]> => {
        if (!state.isReady || !query.trim()) return [];

        setState(prev => ({ ...prev, isSearching: true }));

        return new Promise<SearchResult[]>(async (resolve) => {
            try {
                // If Worker is active, try to use it
                if (workerRef.current) {
                    // Prepare message listener for THIS search
                    const handleResult = async (e: MessageEvent) => {
                        if (e.data.type === 'RESULT') {
                            workerRef.current?.removeEventListener('message', handleResult);

                            const results = e.data.results;

                            if (state.searchMode === 'AI_READY' && results.vector) {
                                // --- GOD TIER LOGIC ---
                                // 1. Worker gave us the Query Vector
                                // 2. We compare against Dexie Vectors
                                const queryVector = results.vector;
                                const allVectors = await db.vectors.toArray();

                                // Cosine Similarity
                                const scored = allVectors.map(v => {
                                    let dot = 0, normA = 0, normB = 0;
                                    for (let i = 0; i < v.vector.length; i++) {
                                        dot += v.vector[i] * queryVector[i];
                                        normA += v.vector[i] * v.vector[i];
                                        normB += queryVector[i] * queryVector[i];
                                    }
                                    const sim = dot / (Math.sqrt(normA) * Math.sqrt(normB));
                                    return { id: v.guidelineId, score: sim };
                                });

                                // Sort & Top K
                                const topIds = scored
                                    .sort((a, b) => b.score - a.score)
                                    .slice(0, topK)
                                    .map(s => s.id);

                                // Fetch guidelines
                                const guidelines = await db.guidelines.bulkGet(topIds);
                                const finalResults = guidelines
                                    .map((g, idx) => g ? { ...g, score: scored.find(s => s.id === g.id)?.score || 0 } : null)
                                    .filter(Boolean) as SearchResult[];

                                resolve(finalResults.sort((a, b) => b.score - a.score));

                            } else {
                                // --- TOY TIER LOGIC ---
                                // Worker filtering (or we could do it here)
                                // If worker handles it, we take results directly
                                // Wait, we need to pass documents to worker for Basic Mode?
                                // Or just do Basic Mode HERE to save complexity
                                // Let's do Basic Mode HERE since we have DB access easily

                                // Actually the prompt said Worker handles "BASIC_MODE".
                                // But worker doesn't have DB access.
                                // So we need to fetch all docs and pass to worker? Inefficient.
                                // BETTER: Do Basic Search HERE in main thread.

                                resolve(results as SearchResult[]);
                            }

                            setState(prev => ({ ...prev, isSearching: false }));
                        }
                    };

                    // Temporarily attach specific listener (simplification)
                    // Ideally we use IDs for messages
                    workerRef.current.addEventListener('message', handleResult);

                    if (state.searchMode === 'AI_READY') {
                        workerRef.current.postMessage({ type: 'SEARCH', query });
                    } else {
                        // BASIC MODE: We need to pass data or do it here. 
                        // To strictly follow prompt "Worker handles BOTH":
                        // We must pass documents.
                        const allDocs = await db.guidelines.toArray();
                        workerRef.current.postMessage({ type: 'SEARCH', query, documents: allDocs });
                    }

                } else {
                    resolve([]);
                }

            } catch (err) {
                console.error('Search error:', err);
                resolve([]);
                setState(prev => ({ ...prev, isSearching: false }));
            }
        });

    }, [state.isReady, state.searchMode]);

    return { ...state, search };
}
