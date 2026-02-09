'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { db, seedDatabase, type Guideline } from '../db/janani.db';

// Types
export interface SearchResult extends Guideline {
    score: number;
}

interface JananiBrainState {
    isReady: boolean;
    isLoading: boolean;
    isSearching: boolean;
    searchMode: 'AI_READY' | 'BASIC_MODE';
    modelStatus: string;
    error: string | null;
}

export function useJananiBrain() {
    const [state, setState] = useState<JananiBrainState>({
        isReady: false,
        isLoading: true,
        isSearching: false,
        searchMode: 'BASIC_MODE',
        modelStatus: 'শুরু হচ্ছে...',
        error: null
    });

    const workerRef = useRef<Worker | null>(null);

    useEffect(() => {
        let isMounted = true;

        async function initialize() {
            try {
                // Seed database
                if (isMounted) setState(prev => ({ ...prev, modelStatus: 'ডাটাবেস লোড হচ্ছে...' }));
                await seedDatabase();

                // Initialize Worker (Static Vanilla JS - Module)
                if (isMounted) setState(prev => ({ ...prev, modelStatus: 'AI মডেল লোড হচ্ছে (0%)...' }));

                workerRef.current = new Worker('/search.worker.js', { type: 'module' });

                // TIMEOUT: Fallback to BASIC_MODE after 30 seconds if AI doesn't load
                const fallbackTimeout = setTimeout(() => {
                    console.warn('[JananiBrain] AI Timeout! Falling back to Basic Mode.');
                    if (isMounted) {
                        setState(prev => ({
                            ...prev,
                            isReady: true,
                            isLoading: false,
                            searchMode: 'BASIC_MODE',
                            modelStatus: '🟠 সাধারণ সার্চ (Timeout)',
                            error: 'AI took too long'
                        }));
                    }
                }, 30000); // 30 second timeout

                workerRef.current.onmessage = async (event) => {
                    const { type, mode, payload, results, error } = event.data;

                    // Handle VECTORS_GENERATED - Save to IndexedDB
                    if (type === 'VECTORS_GENERATED') {
                        console.log(`[JananiBrain] 💾 Saving ${payload.length} vectors to Dexie...`);
                        try {
                            await db.vectors.clear();
                            await db.vectors.bulkPut(payload);
                            console.log('[JananiBrain] ✅ Vectors saved to IndexedDB!');
                        } catch (err) {
                            console.error('[JananiBrain] ❌ Failed to save vectors:', err);
                        }
                    }

                    if (type === 'STATUS') {
                        clearTimeout(fallbackTimeout);

                        if (mode === 'AI_READY') {
                            console.log('[JananiBrain] Worker reports: AI_READY');
                            if (isMounted) {
                                setState({
                                    isReady: true,
                                    isLoading: false,
                                    isSearching: false,
                                    searchMode: 'AI_READY',
                                    modelStatus: '🟢 AI সার্চ (God Tier)',
                                    error: null
                                });
                            }
                        } else {
                            console.log('[JananiBrain] Worker reports: BASIC_MODE');
                            if (isMounted) {
                                setState({
                                    isReady: true,
                                    isLoading: false,
                                    isSearching: false,
                                    searchMode: 'BASIC_MODE',
                                    modelStatus: '🟠 সাধারণ সার্চ',
                                    error: error || 'Worker fell back to basic mode'
                                });
                            }
                        }
                    }
                };

                workerRef.current.onerror = (error) => {
                    console.error('[JananiBrain] Worker error:', error);
                    clearTimeout(fallbackTimeout);
                    if (isMounted) {
                        setState({
                            isReady: true,
                            isLoading: false,
                            isSearching: false,
                            searchMode: 'BASIC_MODE',
                            modelStatus: '🟠 সাধারণ সার্চ (Worker Error)',
                            error: 'Worker failed to initialize'
                        });
                    }
                };

                // ==============================================
                // 🧠 SMART INIT: Check IndexedDB for cached vectors
                // ==============================================
                const existingVectorCount = await db.vectors.count();

                if (existingVectorCount > 0) {
                    // ✅ Vectors exist! Load from IndexedDB and send to worker
                    console.log(`[JananiBrain] 📦 Found ${existingVectorCount} cached vectors, loading to worker...`);

                    const existingVectors = await db.vectors.toArray();
                    const guidelines = await db.guidelines.toArray();
                    const guidelinesMap = new Map(guidelines.map(g => [g.id, g]));

                    // Reconstruct vectors with item data
                    const vectorsWithItems = existingVectors.map(v => ({
                        guidelineId: v.guidelineId,
                        vector: v.vector,
                        item: guidelinesMap.get(v.guidelineId) || null
                    }));

                    workerRef.current.postMessage({
                        type: 'LOAD_VECTORS',
                        payload: { vectors: vectorsWithItems }
                    });
                } else {
                    // ❌ No cached vectors, need to generate
                    console.log('[JananiBrain] 🆕 No cached vectors, generating...');
                    const guidelines = await db.guidelines.toArray();

                    workerRef.current.postMessage({
                        type: 'INIT',
                        payload: { guidelines }
                    });
                }

            } catch (err: any) {
                console.error('[JananiBrain] Init Error:', err);
                if (isMounted) {
                    setState({
                        isReady: true,
                        isLoading: false,
                        isSearching: false,
                        searchMode: 'BASIC_MODE',
                        modelStatus: '🟠 সাধারণ সার্চ',
                        error: err?.message || 'Unknown error'
                    });
                }
            }
        }

        initialize();

        return () => {
            isMounted = false;
            workerRef.current?.terminate();
        };
    }, []);

    // Search Function - Now uses worker for vector search!
    const search = useCallback(async (query: string, topK: number = 5): Promise<SearchResult[]> => {
        if (!state.isReady || !query.trim()) return [];

        setState(prev => ({ ...prev, isSearching: true }));

        return new Promise((resolve) => {
            if (!workerRef.current) {
                setState(prev => ({ ...prev, isSearching: false }));
                resolve([]);
                return;
            }

            // One-time listener for search results
            const handler = (event: MessageEvent) => {
                const { type, results } = event.data;

                if (type === 'RESULT') {
                    workerRef.current?.removeEventListener('message', handler);
                    setState(prev => ({ ...prev, isSearching: false }));
                    resolve(results || []);
                }
            };

            workerRef.current.addEventListener('message', handler);

            // Send search request
            workerRef.current.postMessage({
                type: 'SEARCH',
                payload: { query }
            });

            // Timeout fallback
            setTimeout(() => {
                workerRef.current?.removeEventListener('message', handler);
                setState(prev => ({ ...prev, isSearching: false }));
                resolve([]);
            }, 10000);
        });
    }, [state.isReady]);

    return { ...state, search };
}
