// ============================================================
// 🏥 AR Emergency Labor Assistant - Service Worker
// Offline-First WASM Caching for Rural Bangladesh
// ============================================================

const CACHE_NAME = 'ar-emergency-v2.0';
const WASM_CACHE = 'ar-wasm-v1.0';
const DATA_CACHE = 'ar-data-v1.0';

// Critical assets for offline functionality
const CRITICAL_ASSETS = [
    '/',
    '/ar-dashboard',
    '/static/ar-labor.css',
    '/templates/ar_dashboard.html',
];

// MediaPipe WASM files (CDN - will be cached on first load)
const MEDIAPIPE_ASSETS = [
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/+esm',
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_internal.wasm',
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm/vision_wasm_internal.js',
    'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/ar-labor/stages',
    '/api/ar-labor/emergencies/postpartum_hemorrhage',
    '/api/ar-labor/emergencies/eclampsia',
    '/api/ar-labor/emergencies/cord_prolapse',
    '/api/ar-labor/emergencies/shoulder_dystocia',
    '/api/ar-labor/offline-bundle'
];

// ============ Install Event ============
self.addEventListener('install', event => {
    console.log('🔧 Service Worker installing...');
    
    event.waitUntil(
        Promise.all([
            // Cache critical assets
            caches.open(CACHE_NAME).then(cache => {
                console.log('📦 Caching critical assets...');
                return cache.addAll(CRITICAL_ASSETS);
            }),
            // Pre-cache MediaPipe WASM (on supported browsers)
            caches.open(WASM_CACHE).then(async cache => {
                console.log('🧠 Caching MediaPipe WASM...');
                for (const url of MEDIAPIPE_ASSETS) {
                    try {
                        const response = await fetch(url, { mode: 'cors' });
                        if (response.ok) {
                            await cache.put(url, response);
                            console.log('✅ Cached:', url.substring(0, 60) + '...');
                        }
                    } catch (err) {
                        console.log('⚠️ Could not cache:', url.substring(0, 60) + '...');
                    }
                }
            }),
            // Pre-cache API data for offline use
            caches.open(DATA_CACHE).then(async cache => {
                console.log('📊 Caching API data...');
                for (const endpoint of API_ENDPOINTS) {
                    try {
                        const response = await fetch(endpoint);
                        if (response.ok) {
                            await cache.put(endpoint, response);
                            console.log('✅ Cached API:', endpoint);
                        }
                    } catch (err) {
                        console.log('⚠️ Could not cache API:', endpoint);
                    }
                }
            })
        ]).then(() => {
            console.log('✅ Service Worker installed successfully');
            self.skipWaiting();
        })
    );
});

// ============ Activate Event ============
self.addEventListener('activate', event => {
    console.log('🚀 Service Worker activating...');
    
    event.waitUntil(
        Promise.all([
            // Clean old caches
            caches.keys().then(keys => {
                return Promise.all(
                    keys.filter(key => {
                        return key !== CACHE_NAME && 
                               key !== WASM_CACHE && 
                               key !== DATA_CACHE;
                    }).map(key => {
                        console.log('🗑️ Deleting old cache:', key);
                        return caches.delete(key);
                    })
                );
            }),
            // Take control immediately
            self.clients.claim()
        ])
    );
});

// ============ Fetch Event ============
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    
    // Strategy 1: WASM files - Cache First (never change)
    if (isWasmRequest(event.request)) {
        event.respondWith(wasmCacheFirst(event.request));
        return;
    }
    
    // Strategy 2: API endpoints - Network First, Cache Fallback
    if (isApiRequest(event.request)) {
        event.respondWith(networkFirstWithCache(event.request, DATA_CACHE));
        return;
    }
    
    // Strategy 3: Static assets - Cache First, Network Fallback
    if (isStaticAsset(event.request)) {
        event.respondWith(cacheFirstWithNetwork(event.request, CACHE_NAME));
        return;
    }
    
    // Strategy 4: HTML pages - Network First, Cache Fallback
    if (event.request.mode === 'navigate') {
        event.respondWith(networkFirstWithCache(event.request, CACHE_NAME));
        return;
    }
    
    // Default: Network with cache fallback
    event.respondWith(networkFirstWithCache(event.request, CACHE_NAME));
});

// ============ Caching Strategies ============

// WASM Cache First (for large model files)
async function wasmCacheFirst(request) {
    const cache = await caches.open(WASM_CACHE);
    const cached = await cache.match(request);
    
    if (cached) {
        console.log('💾 WASM from cache:', request.url.substring(0, 60));
        return cached;
    }
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            // Clone and cache
            cache.put(request, response.clone());
            console.log('📥 WASM fetched and cached:', request.url.substring(0, 60));
        }
        return response;
    } catch (err) {
        console.error('❌ WASM fetch failed:', err);
        return new Response('WASM not available offline', { status: 503 });
    }
}

// Network First with Cache Fallback
async function networkFirstWithCache(request, cacheName) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (err) {
        // Network failed, try cache
        const cache = await caches.open(cacheName);
        const cached = await cache.match(request);
        
        if (cached) {
            console.log('📴 Serving from cache (offline):', request.url);
            return cached;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/ar-dashboard') || caches.match('/');
        }
        
        return new Response('Offline - Content not cached', { status: 503 });
    }
}

// Cache First with Network Fallback
async function cacheFirstWithNetwork(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);
    
    if (cached) {
        // Return cached, but update in background
        fetchAndCache(request, cacheName);
        return cached;
    }
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        return new Response('Resource not available', { status: 503 });
    }
}

// Background fetch and cache update
async function fetchAndCache(request, cacheName) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response);
        }
    } catch (err) {
        // Silently fail - we already returned cached version
    }
}

// ============ Request Type Helpers ============

function isWasmRequest(request) {
    const url = request.url;
    return url.includes('.wasm') || 
           url.includes('.task') ||
           url.includes('mediapipe') ||
           url.includes('tasks-vision');
}

function isApiRequest(request) {
    return request.url.includes('/api/');
}

function isStaticAsset(request) {
    const url = request.url;
    return url.includes('/static/') ||
           url.endsWith('.css') ||
           url.endsWith('.js') ||
           url.endsWith('.png') ||
           url.endsWith('.jpg') ||
           url.endsWith('.svg') ||
           url.endsWith('.woff2');
}

// ============ Background Sync ============

self.addEventListener('sync', event => {
    if (event.tag === 'sync-session-data') {
        event.waitUntil(syncSessionData());
    }
});

async function syncSessionData() {
    try {
        // Get pending data from IndexedDB
        const pendingData = await getPendingSessionData();
        
        if (pendingData.length > 0) {
            // Send to server
            const response = await fetch('/api/ar-labor/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessions: pendingData })
            });
            
            if (response.ok) {
                // Clear synced data
                await clearPendingSessionData();
                console.log('✅ Session data synced');
            }
        }
    } catch (err) {
        console.error('❌ Sync failed:', err);
    }
}

// IndexedDB helpers (simplified - real implementation would use idb library)
async function getPendingSessionData() {
    return []; // Placeholder
}

async function clearPendingSessionData() {
    // Placeholder
}

// ============ Push Notifications ============

self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    
    const options = {
        body: data.body || 'জরুরি সতর্কতা',
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/badge-72.png',
        vibrate: [200, 100, 200],
        tag: 'ar-emergency',
        requireInteraction: true,
        actions: [
            { action: 'open', title: 'খুলুন', icon: '/static/icons/open.png' },
            { action: 'call', title: '৯৯৯ কল', icon: '/static/icons/call.png' }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title || '🏥 AR জরুরি সহায়তা', options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'call') {
        // Open dialer with emergency number
        clients.openWindow('tel:999');
    } else {
        // Open AR dashboard
        event.waitUntil(
            clients.matchAll({ type: 'window' }).then(clientList => {
                // Focus existing window or open new
                for (const client of clientList) {
                    if (client.url.includes('/ar-dashboard') && 'focus' in client) {
                        return client.focus();
                    }
                }
                return clients.openWindow('/ar-dashboard');
            })
        );
    }
});

// ============ Message Handler ============

self.addEventListener('message', event => {
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data.type === 'CACHE_WASM') {
        // Manually trigger WASM caching
        caches.open(WASM_CACHE).then(async cache => {
            for (const url of MEDIAPIPE_ASSETS) {
                try {
                    const response = await fetch(url, { mode: 'cors' });
                    if (response.ok) {
                        await cache.put(url, response);
                    }
                } catch (err) {
                    console.log('Could not cache:', url);
                }
            }
            event.source.postMessage({ type: 'WASM_CACHED' });
        });
    }
    
    if (event.data.type === 'GET_CACHE_STATUS') {
        // Return cache status
        Promise.all([
            caches.open(CACHE_NAME).then(c => c.keys()),
            caches.open(WASM_CACHE).then(c => c.keys()),
            caches.open(DATA_CACHE).then(c => c.keys())
        ]).then(([critical, wasm, data]) => {
            event.source.postMessage({
                type: 'CACHE_STATUS',
                critical: critical.length,
                wasm: wasm.length,
                data: data.length
            });
        });
    }
});

console.log('🏥 AR Emergency Service Worker loaded');
