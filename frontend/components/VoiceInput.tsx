'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';

interface VoiceInputProps {
    onResult: (text: string) => void;
    disabled?: boolean;
    className?: string;
}

// TypeScript: Extend Window interface for SpeechRecognition
declare global {
    interface Window {
        SpeechRecognition: typeof SpeechRecognition;
        webkitSpeechRecognition: typeof SpeechRecognition;
    }
}

export default function VoiceInput({ onResult, disabled = false, className = '' }: VoiceInputProps) {
    const [isListening, setIsListening] = useState(false);
    const [isSupported, setIsSupported] = useState(true);
    const recognitionRef = useRef<SpeechRecognition | null>(null);

    // Initialize Speech Recognition
    useEffect(() => {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('[VoiceInput] Speech Recognition not supported');
            setIsSupported(false);
            return;
        }

        const recognition = new SpeechRecognition();

        // Configure for Bangla
        recognition.lang = 'bn-BD'; // Bangla (Bangladesh)
        recognition.continuous = false; // Stop after one sentence
        recognition.interimResults = false; // Only final results
        recognition.maxAlternatives = 1;

        // Event handlers
        recognition.onstart = () => {
            console.log('[VoiceInput] 🎤 Listening started...');
            setIsListening(true);
        };

        recognition.onend = () => {
            console.log('[VoiceInput] 🎤 Listening ended');
            setIsListening(false);
        };

        recognition.onresult = (event: SpeechRecognitionEvent) => {
            const transcript = event.results[0][0].transcript;
            console.log('[VoiceInput] 📝 Transcript:', transcript);
            onResult(transcript);
        };

        recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
            console.error('[VoiceInput] ❌ Error:', event.error);
            setIsListening(false);

            // Show user-friendly error for common cases
            if (event.error === 'no-speech') {
                console.log('[VoiceInput] No speech detected');
            } else if (event.error === 'not-allowed') {
                console.warn('[VoiceInput] Microphone permission denied');
            }
        };

        recognitionRef.current = recognition;

        return () => {
            recognition.abort();
        };
    }, [onResult]);

    // Toggle listening
    const toggleListening = useCallback(() => {
        if (!recognitionRef.current || disabled) return;

        if (isListening) {
            recognitionRef.current.stop();
        } else {
            try {
                recognitionRef.current.start();
            } catch (err) {
                console.error('[VoiceInput] Start error:', err);
            }
        }
    }, [isListening, disabled]);

    // Don't render if not supported
    if (!isSupported) {
        return null;
    }

    return (
        <button
            type="button"
            onClick={toggleListening}
            disabled={disabled}
            title={isListening ? 'শোনা বন্ধ করুন' : 'কথা বলুন (বাংলায়)'}
            className={`
                flex items-center justify-center
                w-10 h-10 rounded-full
                transition-all duration-300 ease-in-out
                ${isListening
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-500/50'
                    : 'bg-pink-500 hover:bg-pink-600'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                text-white
                ${className}
            `}
        >
            {isListening ? (
                // Listening icon (waves)
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                    <circle cx="12" cy="11" r="1" className="animate-ping" />
                </svg>
            ) : (
                // Microphone icon
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
                </svg>
            )}
        </button>
    );
}
