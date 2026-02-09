'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useJananiBrain, type SearchResult } from '../src/hooks/useJananiBrain';
import { ErrorBoundary } from 'react-error-boundary';
import RobotVoice from './RobotVoice';

// Medical Card Component
function MedicalCard({ result }: { result: SearchResult }) {
    const getActionBadgeColor = (actionType: string) => {
        switch (actionType) {
            case 'emergency': return 'bg-red-500';
            case 'warning': return 'bg-yellow-500';
            case 'info': return 'bg-blue-500';
            default: return 'bg-gray-500';
        }
    };

    const getActionLabel = (actionType: string) => {
        switch (actionType) {
            case 'emergency': return 'জরুরি';
            case 'warning': return 'সতর্কতা';
            case 'info': return 'তথ্য';
            default: return actionType;
        }
    };

    const scorePercent = Math.round(result.score * 100);

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700 transition-all hover:shadow-xl">
            {/* Header with badge and score */}
            <div className="flex justify-between items-start mb-3">
                <span className={`${getActionBadgeColor(result.action_type)} text-white text-xs font-bold px-3 py-1 rounded-full`}>
                    {getActionLabel(result.action_type)}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                    {scorePercent}% মিল
                </span>
            </div>

            {/* Title */}
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {result.title}
            </h3>

            {/* Text */}
            <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                {result.text}
            </p>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-4">
                {result.tags.map((tag, idx) => (
                    <span
                        key={idx}
                        className="bg-pink-100 dark:bg-pink-900 text-pink-800 dark:text-pink-200 text-xs px-2 py-1 rounded-full"
                    >
                        {tag}
                    </span>
                ))}
            </div>

            {/* Nutrition tags if present */}
            {result.nutrition_tags && result.nutrition_tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                    {result.nutrition_tags.map((tag, idx) => (
                        <span
                            key={idx}
                            className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs px-2 py-1 rounded-full"
                        >
                            🥗 {tag.replace('_', ' ')}
                        </span>
                    ))}
                </div>
            )}

            {/* RobotVoice button */}
            {result.speech_text && (
                <RobotVoice text={result.speech_text} />
            )}
        </div>
    );
}

// Error Fallback Component
function ErrorFallback({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) {
    return (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 text-center">
            <h3 className="text-red-800 dark:text-red-200 font-bold mb-2">কিছু সমস্যা হয়েছে</h3>
            <p className="text-red-600 dark:text-red-300 text-sm mb-4">{error.message}</p>
            <button
                onClick={resetErrorBoundary}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg"
            >
                আবার চেষ্টা করুন
            </button>
        </div>
    );
}

function JananiSearchInner() {
    const { isReady, isLoading, isSearching, modelStatus, error, search } = useJananiBrain();
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [hasSearched, setHasSearched] = useState(false);
    const debounceRef = useRef<NodeJS.Timeout | null>(null);

    // Handle search with debounce
    const handleSearch = useCallback(async (searchQuery: string) => {
        if (!searchQuery.trim()) {
            setResults([]);
            setHasSearched(false);
            return;
        }

        setHasSearched(true);
        const searchResults = await search(searchQuery, 5);
        setResults(searchResults);
    }, [search]);

    // Debounced input handler
    const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setQuery(value);

        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }

        debounceRef.current = setTimeout(() => {
            handleSearch(value);
        }, 300);
    }, [handleSearch]);

    // Cleanup
    useEffect(() => {
        return () => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
        };
    }, []);

    return (
        <div className="max-w-3xl mx-auto p-6">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-pink-500 to-rose-600 bg-clip-text text-transparent mb-2">
                    🧠 জানানী ব্রেইন
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                    অফলাইন স্বাস্থ্য গাইড সার্চ
                </p>
            </div>

            {/* Status indicator */}
            <div className="flex items-center justify-center gap-2 mb-6">
                <div className={`w-3 h-3 rounded-full ${isReady ? 'bg-green-500' : isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                    {error || modelStatus}
                </span>
            </div>

            {/* Search bar */}
            <div className="relative mb-8">
                <input
                    type="text"
                    value={query}
                    onChange={handleInputChange}
                    placeholder="লক্ষণ লিখুন... (যেমন: 'মাথা ব্যথা', 'জ্বর', 'রক্তপাত')"
                    disabled={!isReady}
                    className="w-full px-6 py-4 text-lg rounded-2xl border-2 border-pink-200 dark:border-pink-800 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:border-pink-500 focus:outline-none focus:ring-4 focus:ring-pink-100 dark:focus:ring-pink-900 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                />
                {isSearching && (
                    <div className="absolute right-4 top-1/2 -translate-y-1/2">
                        <div className="w-6 h-6 border-2 border-pink-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                )}
            </div>

            {/* Results */}
            {hasSearched && (
                <div className="space-y-4">
                    {results.length > 0 ? (
                        results.map((result) => (
                            <MedicalCard
                                key={result.id}
                                result={result}
                            />
                        ))
                    ) : (
                        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                            <p className="text-lg">কোনো তথ্য পাওয়া যায়নি</p>
                            <p className="text-sm">অন্য কিছু লিখে দেখুন</p>
                        </div>
                    )}
                </div>
            )}

            {/* Initial state */}
            {!hasSearched && isReady && (
                <div className="text-center py-12 text-gray-400 dark:text-gray-500">
                    <p className="text-lg">আপনার সমস্যা লিখুন</p>
                    <p className="text-sm mt-2">যেমন: "মাথা ব্যথা", "জ্বর", "রক্তপাত"</p>
                </div>
            )}
        </div>
    );
}

// Wrapped with Error Boundary
export default function JananiSearch() {
    return (
        <ErrorBoundary FallbackComponent={ErrorFallback} onReset={() => window.location.reload()}>
            <JananiSearchInner />
        </ErrorBoundary>
    );
}
