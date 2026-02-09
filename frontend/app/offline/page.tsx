'use client';

import JananiSearch from '../../components/JananiSearch';

export default function OfflinePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 dark:from-gray-900 dark:to-purple-900 py-12">
            <div className="container mx-auto px-4">
                <JananiSearch />
            </div>
        </div>
    );
}
