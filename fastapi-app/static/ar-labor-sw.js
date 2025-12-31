/**
 * AR Emergency Labor Assistant - Offline-First Service Worker
 * Caches all critical resources for offline use in rural Bangladesh
 */

const CACHE_NAME = 'janani-ar-labor-v1';
const OFFLINE_DATA_KEY = 'ar_labor_offline_data';

// Resources to cache for offline use
const STATIC_ASSETS = [
    '/',
    '/static/ar-labor.js',
    '/static/ar-labor.css',
    '/api/ar-labor/offline-bundle',
    // MediaPipe models (bundled)
    'https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose_solution_packed_assets.data',
    'https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose_solution_simd_wasm_bin.wasm'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing AR Labor Service Worker...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_ASSETS.filter(url => !url.startsWith('http')));
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating AR Labor Service Worker...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // Handle API requests specially
    if (url.pathname.startsWith('/api/ar-labor/')) {
        event.respondWith(handleAPIRequest(event.request));
        return;
    }
    
    // For other requests, try network first, fall back to cache
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Cache successful responses
                if (response.ok) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // Offline - try cache
                return caches.match(event.request);
            })
    );
});

// Handle AR Labor API requests
async function handleAPIRequest(request) {
    const url = new URL(request.url);
    
    try {
        // Try network first
        const response = await fetch(request);
        
        // Cache the response for offline use
        if (response.ok) {
            const responseClone = response.clone();
            const cache = await caches.open(CACHE_NAME);
            await cache.put(request, responseClone);
        }
        
        return response;
    } catch (error) {
        console.log('[SW] Network failed, serving from cache:', url.pathname);
        
        // Try to serve from cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // If no cache, return offline-friendly error
        return new Response(JSON.stringify({
            success: false,
            offline: true,
            message_bn: '📴 অফলাইন মোড - ক্যাশ থেকে ডেটা দেখানো হচ্ছে',
            message_en: '📴 Offline mode - showing cached data'
        }), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    if (event.tag === 'sync-session-log') {
        event.waitUntil(syncSessionLog());
    }
});

// Sync offline session logs to server
async function syncSessionLog() {
    try {
        // Get pending logs from IndexedDB
        const db = await openIndexedDB();
        const logs = await getPendingLogs(db);
        
        if (logs.length === 0) {
            console.log('[SW] No pending logs to sync');
            return;
        }
        
        console.log('[SW] Syncing', logs.length, 'log entries');
        
        // Send to server
        const response = await fetch('/api/ar-labor/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_log: logs,
                device_id: 'device_' + Date.now(),
                timestamp: new Date().toISOString()
            })
        });
        
        if (response.ok) {
            // Clear synced logs
            await clearSyncedLogs(db, logs);
            console.log('[SW] Sync complete');
            
            // Notify client
            self.clients.matchAll().then(clients => {
                clients.forEach(client => {
                    client.postMessage({
                        type: 'SYNC_COMPLETE',
                        count: logs.length
                    });
                });
            });
        }
    } catch (error) {
        console.error('[SW] Sync failed:', error);
    }
}

// IndexedDB helpers
function openIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('JananiARLabor', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            // Create stores
            if (!db.objectStoreNames.contains('session_logs')) {
                db.createObjectStore('session_logs', { keyPath: 'id', autoIncrement: true });
            }
            if (!db.objectStoreNames.contains('offline_data')) {
                db.createObjectStore('offline_data', { keyPath: 'key' });
            }
        };
    });
}

function getPendingLogs(db) {
    return new Promise((resolve, reject) => {
        const tx = db.transaction('session_logs', 'readonly');
        const store = tx.objectStore('session_logs');
        const request = store.getAll();
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function clearSyncedLogs(db, logs) {
    return new Promise((resolve, reject) => {
        const tx = db.transaction('session_logs', 'readwrite');
        const store = tx.objectStore('session_logs');
        
        logs.forEach(log => {
            store.delete(log.id);
        });
        
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

// Listen for messages from main thread
self.addEventListener('message', (event) => {
    if (event.data.type === 'CACHE_OFFLINE_DATA') {
        cacheOfflineData(event.data.data);
    }
});

async function cacheOfflineData(data) {
    const db = await openIndexedDB();
    const tx = db.transaction('offline_data', 'readwrite');
    const store = tx.objectStore('offline_data');
    
    store.put({
        key: OFFLINE_DATA_KEY,
        data: data,
        timestamp: new Date().toISOString()
    });
    
    console.log('[SW] Offline data cached successfully');
}
