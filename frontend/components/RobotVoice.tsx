'use client';

import React, { useState, useCallback, useEffect, useRef } from 'react';

interface RobotVoiceProps {
    text: string;
    className?: string;
}

export default function RobotVoice({ text, className = '' }: RobotVoiceProps) {
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
    const [isReady, setIsReady] = useState(false);
    const [activeVoice, setActiveVoice] = useState<SpeechSynthesisVoice | null>(null);
    const voiceLoadAttempts = useRef(0);

    // Robust voice loading
    useEffect(() => {
        const loadVoices = () => {
            const availableVoices = window.speechSynthesis.getVoices();
            if (availableVoices.length > 0) {
                setVoices(availableVoices);
                setIsReady(true);
            } else {
                voiceLoadAttempts.current++;
                if (voiceLoadAttempts.current < 10) setTimeout(loadVoices, 200);
                else setIsReady(true);
            }
        };
        loadVoices();
        window.speechSynthesis.onvoiceschanged = loadVoices;
        return () => { window.speechSynthesis.onvoiceschanged = null; };
    }, []);

    // Select best voice and update state
    useEffect(() => {
        if (voices.length === 0) return;

        const priorities = [
            (v: SpeechSynthesisVoice) => v.lang === 'bn-BD',
            (v: SpeechSynthesisVoice) => v.lang === 'bn-IN',
            (v: SpeechSynthesisVoice) => v.lang.startsWith('bn'),
            (v: SpeechSynthesisVoice) => v.name.toLowerCase().includes('bangla') || v.name.toLowerCase().includes('bengali'),
            (v: SpeechSynthesisVoice) => v.lang === 'hi-IN',
            (v: SpeechSynthesisVoice) => v.lang.startsWith('hi'),
            (v: SpeechSynthesisVoice) => v.name.toLowerCase().includes('hindi'),
        ];

        let selected = null;
        for (const check of priorities) {
            selected = voices.find(check);
            if (selected) break;
        }
        setActiveVoice(selected || null);
    }, [voices]);

    const handleSpeak = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
        if (!('speechSynthesis' in window)) {
            alert('আপনার ব্রাউজারে স্পিচ সাপোর্ট নেই।');
            return;
        }
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;

        if (activeVoice) {
            utterance.voice = activeVoice;
            utterance.lang = activeVoice.lang;
        } else {
            utterance.lang = 'hi-IN'; // Fallback
        }

        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utterance);
    }, [text, activeVoice]);

    const handleStop = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
    }, []);

    const showDebug = useCallback((e: React.MouseEvent) => {
        e.stopPropagation();
        const detected = voices
            .filter(v => v.lang.startsWith('bn') || v.lang.startsWith('hi') || v.name.includes('Bangla') || v.name.includes('Bengali') || v.name.includes('Hindi'))
            .map(v => `• ${v.name} (${v.lang})`)
            .join('\n');

        const statusMsg = activeVoice
            ? `✅ Active Voice: ${activeVoice.name}\n`
            : `❌ No Bangla/Hindi voice detected.\nUsing System Default.\n`;

        alert(
            `${statusMsg}\n` +
            `Detected Relevant Voices:\n${detected || 'None'}\n\n` +
            `Total Installed: ${voices.length}\n\n` +
            `To fix: Install 'Bengali (Bangladesh)' in Windows Settings > Time & Language > Speech.`
        );
    }, [voices, activeVoice]);

    // Badge logic
    const getBadge = () => {
        if (!isReady) return { text: '...', color: 'bg-gray-200' };
        if (!activeVoice) return { text: '⚠️', color: 'bg-yellow-100 text-yellow-800' };
        if (activeVoice.lang.startsWith('bn')) return { text: 'BN', color: 'bg-green-100 text-green-800' };
        if (activeVoice.lang.startsWith('hi')) return { text: 'HI', color: 'bg-orange-100 text-orange-800' };
        return { text: '?', color: 'bg-gray-200' };
    };

    const badge = getBadge();

    return (
        <div className="flex items-center gap-2">
            <button
                onClick={isSpeaking ? handleStop : handleSpeak}
                disabled={!isReady}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${isSpeaking
                    ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                    : 'bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white'
                    } ${!isReady ? 'opacity-50 cursor-wait' : ''} ${className}`}
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

            {/* Always visible debug badge */}
            <button
                onClick={showDebug}
                className={`text-xs font-bold px-2 py-1 rounded-full border border-current opacity-80 hover:opacity-100 transition-all ${badge.color}`}
                title="Current Voice Info & Debug"
            >
                {badge.text}
            </button>
        </div>
    );
}
