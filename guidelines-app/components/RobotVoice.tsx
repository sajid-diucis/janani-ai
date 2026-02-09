'use client';

import React, { useState, useCallback, useEffect } from 'react';

interface RobotVoiceProps {
    text: string;
    className?: string;
}

export default function RobotVoice({ text, className = '' }: RobotVoiceProps) {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

    // Load voices when available
    useEffect(() => {
        const loadVoices = () => {
            const availableVoices = window.speechSynthesis.getVoices();
            setVoices(availableVoices);
        };

        // Voices might not be available immediately
        loadVoices();
        window.speechSynthesis.onvoiceschanged = loadVoices;

        return () => {
            window.speechSynthesis.onvoiceschanged = null;
        };
    }, []);

    const handleSpeak = useCallback(() => {
        if (!('speechSynthesis' in window)) {
            console.warn('[RobotVoice] Speech synthesis not supported');
            return;
        }

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        // Configure for Bangla
        utterance.rate = 0.85; // Slower for Bangla clarity
        utterance.pitch = 1.1;
        utterance.volume = 1.0;
        utterance.lang = 'bn-BD'; // Bangla (Bangladesh)

        // Try to find Bangla voice, fallback to Hindi (similar script)
        const banglaVoice = voices.find(v =>
            v.lang === 'bn-BD' ||
            v.lang === 'bn-IN' ||
            v.lang.startsWith('bn') ||
            v.name.includes('Bangla') ||
            v.name.includes('Bengali')
        );

        const hindiVoice = voices.find(v =>
            v.lang === 'hi-IN' ||
            v.lang.startsWith('hi') ||
            v.name.includes('Hindi')
        );

        if (banglaVoice) {
            utterance.voice = banglaVoice;
            console.log('[RobotVoice] Using Bangla voice:', banglaVoice.name);
        } else if (hindiVoice) {
            utterance.voice = hindiVoice;
            console.log('[RobotVoice] Using Hindi voice as fallback:', hindiVoice.name);
        } else {
            console.log('[RobotVoice] No Bangla/Hindi voice found, using default');
        }

        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = (e) => {
            console.warn('[RobotVoice] Speech error:', e);
            setIsSpeaking(false);
        };

        window.speechSynthesis.speak(utterance);
    }, [text, voices]);

    const handleStop = useCallback(() => {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
    }, []);

    return (
        <button
            onClick={isSpeaking ? handleStop : handleSpeak}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${isSpeaking
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white'
                } ${className}`}
            title={isSpeaking ? 'বন্ধ করুন' : 'শুনুন'}
        >
            {isSpeaking ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                </svg>
            ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clipRule="evenodd" />
                </svg>
            )}
            {isSpeaking ? 'বন্ধ' : 'শুনুন'}
        </button>
    );
}
