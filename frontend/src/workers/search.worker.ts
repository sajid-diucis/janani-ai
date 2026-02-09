import { pipeline, env } from '@xenova/transformers';

// 1. Force Local Mode
env.allowLocalModels = true;
env.allowRemoteModels = false;
env.localModelPath = '/models/';

let extractor: any = null;
let guideVectors: any[] = [];

// Cosine similarity function
function cosineSimilarity(a: number[], b: number[]) {
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

self.onmessage = async (e) => {
    const { type, payload } = e.data;

    // ============================================
    // LOAD_VECTORS: Load pre-existing vectors from IndexedDB into memory
    // ============================================
    if (type === 'LOAD_VECTORS') {
        try {
            console.log("🧠 Worker: Loading Model...");
            extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2', {
                quantized: true,
            });

            // Load vectors into memory
            const vectors = payload.vectors || [];
            guideVectors = vectors;

            console.log(`📥 Worker: Loaded ${guideVectors.length} vectors into memory from IndexedDB`);

            postMessage({ type: 'STATUS', mode: 'AI_READY' });

        } catch (err) {
            console.error("❌ Worker Error (LOAD_VECTORS):", err);
            postMessage({ type: 'STATUS', mode: 'BASIC_MODE' });
        }
    }

    // ============================================
    // INIT: Generate new vectors (first-time setup)
    // ============================================
    if (type === 'INIT') {
        try {
            // A. Load the Brain (23.7 MB Cache)
            console.log("🧠 Worker: Loading Model...");
            extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2', {
                quantized: true,
            });

            // B. Load the Data
            const rawGuidelines = payload.guidelines || [];

            // C. Generate vectors
            console.log("⚡ Worker: Generating Vectors for " + rawGuidelines.length + " items...");

            guideVectors = [];
            for (const item of rawGuidelines) {
                const content = `${item.title} ${item.text} ${item.tags.join(' ')}`;
                const output = await extractor(content, { pooling: 'mean', normalize: true });

                guideVectors.push({
                    guidelineId: item.id, // Match your DB schema
                    vector: output.data,
                    item: item
                });
            }

            console.log("✅ Worker: Math complete. Sending vectors to Main Thread to save...");

            // D. Send Vectors back to Main Thread to save in Dexie
            postMessage({ type: 'VECTORS_GENERATED', payload: guideVectors });

            postMessage({ type: 'STATUS', mode: 'AI_READY' });

        } catch (err) {
            console.error("❌ Worker Error (INIT):", err);
            postMessage({ type: 'STATUS', mode: 'BASIC_MODE' });
        }
    }

    // ============================================
    // SEARCH: Perform semantic or keyword search
    // ============================================
    if (type === 'SEARCH') {
        const { query, documents } = payload || {};

        try {
            if (extractor && guideVectors.length > 0) {
                // --- GOD TIER: VECTOR SEARCH ---
                console.log(`[Worker] Performing Vector Search on ${guideVectors.length} items...`);

                // Generate query embedding
                const output = await extractor(query, { pooling: 'mean', normalize: true });
                const queryVector = Array.from(output.data) as number[];

                // Calculate similarity scores
                const scoredResults = guideVectors.map((item: any) => {
                    const itemVector = Array.from(item.vector) as number[];
                    const score = cosineSimilarity(queryVector, itemVector);
                    return { ...item.item, score };
                });

                // Sort by score descending and take top 5
                const topResults = scoredResults
                    .sort((a: any, b: any) => b.score - a.score)
                    .slice(0, 5);

                console.log(`[Worker] Found ${topResults.length} results`);

                self.postMessage({
                    type: 'RESULTS',
                    payload: topResults
                });

            } else if (extractor) {
                // AI ready but no vectors in memory - return just the query vector
                console.log('[Worker] WARNING: AI ready but guideVectors is empty!');
                const output = await extractor(query, { pooling: 'mean', normalize: true });
                const queryVector = Array.from(output.data) as number[];

                self.postMessage({
                    type: 'RESULT',
                    results: { vector: queryVector }
                });

            } else {
                // --- TOY TIER: KEYWORD SEARCH ---
                console.log('[Worker] Performing Keyword Search...');
                if (documents) {
                    const lowerQuery = query.toLowerCase();
                    const results = documents.filter((doc: any) => {
                        const content = `${doc.title} ${doc.text} ${doc.tags?.join(' ')}`.toLowerCase();
                        return content.includes(lowerQuery);
                    });
                    self.postMessage({ type: 'RESULTS', payload: results });
                } else {
                    self.postMessage({ type: 'ERROR', error: 'No documents provided for keyword search' });
                }
            }
        } catch (err: any) {
            console.error('[Worker] Search error:', err);
            self.postMessage({ type: 'ERROR', error: err.message });
        }
    }
};
