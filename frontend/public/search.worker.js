// 🚀 OFFLINE MODE: Load libraries via ESM
import { pipeline, env } from '/libs/transformers.min.js';

// 🛑 CRITICAL CONFIGURATION (Matches user requirements)
env.allowLocalModels = true;
env.allowRemoteModels = false; // Force Offline
env.localModelPath = '/models/'; // Path to local models
env.useBrowserCache = true;

// 🛑 WASM CONFIGURATION
env.backends.onnx.wasm.wasmPaths = '/wasm/';
env.backends.onnx.wasm.numThreads = 1;

console.log('[Worker] Vanilla JS Worker Started');
console.log('[Worker] Config:', { localPath: env.localModelPath, wasmPath: env.backends.onnx.wasm.wasmPaths });

let extractor = null;
let guideVectors = []; // 🧠 MEMORY: Store vectors here!

// Cosine similarity function
function cosineSimilarity(a, b) {
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    for (let i = 0; i < a.length; i++) {
        dotProduct += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// Auto-initialize Model ONLY
async function initModel() {
    try {
        console.log('[Worker] 🧠 Loading AI Model...');
        extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2', {
            quantized: true,
            progress_callback: (data) => {
                if (data.status === 'progress') {
                    console.log(`[Worker] Loading: ${Math.round(data.progress || 0)}%`);
                }
            }
        });
        console.log('[Worker] ✅ AI Model Ready');
        return true;
    } catch (e) {
        console.error('[Worker] ❌ Model Init Failed:', e);
        return false;
    }
}

self.onmessage = async (e) => {
    const { type, payload } = e.data;

    // ============================================
    // INIT: Load model + generate vectors (first time)
    // ============================================
    if (type === 'INIT') {
        const modelReady = await initModel();

        if (!modelReady) {
            self.postMessage({ type: 'STATUS', mode: 'BASIC_MODE', error: 'Model failed to load' });
            return;
        }

        const guidelines = payload?.guidelines || [];

        if (guidelines.length > 0) {
            // Generate vectors for first time
            console.log(`[Worker] ⚡ Generating vectors for ${guidelines.length} items...`);
            guideVectors = [];

            for (const item of guidelines) {
                const content = `${item.title} ${item.text} ${item.tags.join(' ')}`;
                const output = await extractor(content, { pooling: 'mean', normalize: true });

                guideVectors.push({
                    guidelineId: item.id,
                    vector: Array.from(output.data),
                    item: item
                });
            }

            console.log(`[Worker] ✅ Generated ${guideVectors.length} vectors`);

            // Send vectors back to main thread to save in Dexie
            self.postMessage({ type: 'VECTORS_GENERATED', payload: guideVectors });
        }

        self.postMessage({ type: 'STATUS', mode: 'AI_READY' });
    }

    // ============================================
    // LOAD_VECTORS: Load pre-existing vectors from IndexedDB
    // ============================================
    else if (type === 'LOAD_VECTORS') {
        const modelReady = await initModel();

        if (!modelReady) {
            self.postMessage({ type: 'STATUS', mode: 'BASIC_MODE', error: 'Model failed to load' });
            return;
        }

        const vectors = payload?.vectors || [];
        guideVectors = vectors;

        console.log(`[Worker] 📥 Loaded ${guideVectors.length} vectors into memory from IndexedDB`);
        self.postMessage({ type: 'STATUS', mode: 'AI_READY' });
    }

    // ============================================
    // SEARCH: Perform semantic search using vectors
    // ============================================
    else if (type === 'SEARCH') {
        const query = payload?.query || e.data.query; // Support both formats

        if (!extractor) {
            console.log('[Worker] ❌ Extractor not ready');
            self.postMessage({ type: 'RESULT', results: [] });
            return;
        }

        if (guideVectors.length === 0) {
            console.log('[Worker] ⚠️ WARNING: guideVectors is empty! Cannot perform vector search.');
            self.postMessage({ type: 'RESULT', results: [] });
            return;
        }

        try {
            console.log(`[Worker] 🔍 Searching "${query}" across ${guideVectors.length} vectors...`);

            // Generate query embedding
            const output = await extractor(query, { pooling: 'mean', normalize: true });
            const queryVector = Array.from(output.data);

            // Calculate similarity scores
            const scoredResults = guideVectors.map((item) => {
                const itemVector = Array.isArray(item.vector) ? item.vector : Array.from(item.vector);
                const score = cosineSimilarity(queryVector, itemVector);
                return { ...item.item, score };
            });

            // Sort by score descending and take top 5
            const topResults = scoredResults
                .sort((a, b) => b.score - a.score)
                .slice(0, 5);

            console.log(`[Worker] ✅ Found ${topResults.length} results`);

            self.postMessage({
                type: 'RESULT',
                results: topResults
            });
        } catch (err) {
            console.error('[Worker] Search Error:', err);
            self.postMessage({ type: 'ERROR', error: err.message });
        }
    }
};
