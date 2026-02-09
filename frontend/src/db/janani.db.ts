import Dexie, { type Table } from 'dexie';

// Interfaces based on who_guidelines.json schema
export interface Guideline {
    id: string;
    title: string;
    text: string;
    tags: string[];
    speech_text?: string;
    nutrition_tags?: string[];
    action_type: string;
}

export interface GuidelineVector {
    id?: number;
    guidelineId: string;
    vector: Float32Array;
}

// Dexie Database class
class JananiDatabase extends Dexie {
    guidelines!: Table<Guideline, string>;
    vectors!: Table<GuidelineVector, number>;

    constructor() {
        super('JananiOfflineDB');

        this.version(1).stores({
            // Primary key is 'id', indexed fields: title, action_type, *tags (multi-entry)
            guidelines: 'id, title, action_type, *tags',
            // Primary key is auto-increment 'id', indexed: guidelineId
            // NOTE: 'vector' is NOT indexed (too large, not searchable by index)
            vectors: '++id, guidelineId'
        });
    }
}

// Singleton database instance
export const db = new JananiDatabase();

// Seed the database from who_guidelines.json (ONLY stores guidelines, NO embeddings)
// Embeddings are generated on-demand when AI is ready
export async function seedDatabase(): Promise<void> {
    try {
        // Check if database already has data
        const existingCount = await db.guidelines.count();
        if (existingCount > 0) {
            console.log('[JananiBrain] Database already seeded with', existingCount, 'guidelines');
            return;
        }

        console.log('[JananiBrain] Seeding database...');

        // Fetch guidelines data
        const response = await fetch('/data/who_guidelines.json');
        if (!response.ok) {
            throw new Error(`Failed to fetch guidelines: ${response.status}`);
        }

        const guidelines: Guideline[] = await response.json();
        console.log('[JananiBrain] Loaded', guidelines.length, 'guidelines');

        // Store guidelines ONLY (embeddings will be generated when AI is ready)
        await db.guidelines.bulkPut(guidelines);
        console.log('[JananiBrain] Guidelines stored in IndexedDB');
        console.log('[JananiBrain] Database seeding complete! (Embeddings will be generated when AI loads)');

    } catch (error) {
        console.error('[JananiBrain] Seeding failed:', error);
        throw error;
    }
}

// Generate embeddings for all guidelines (called separately when AI is ready)
export async function generateAllEmbeddings(
    embeddingFn: (text: string) => Promise<Float32Array>
): Promise<void> {
    const existingVectors = await db.vectors.count();
    if (existingVectors > 0) {
        console.log('[JananiBrain] Embeddings already exist:', existingVectors);
        return;
    }

    const guidelines = await db.guidelines.toArray();
    console.log('[JananiBrain] Generating embeddings for', guidelines.length, 'guidelines...');

    for (const guideline of guidelines) {
        const textToEmbed = `${guideline.title}. ${guideline.text}. ${guideline.tags.join(', ')}`;

        try {
            const vector = await embeddingFn(textToEmbed);
            await db.vectors.add({
                guidelineId: guideline.id,
                vector: vector
            });
            console.log('[JananiBrain] Embedded:', guideline.id);
        } catch (error) {
            console.error('[JananiBrain] Failed to embed:', guideline.id, error);
        }
    }

    console.log('[JananiBrain] All embeddings generated!');
}

// Clear database (for debugging)
export async function clearDatabase(): Promise<void> {
    await db.guidelines.clear();
    await db.vectors.clear();
    console.log('[JananiBrain] Database cleared');
}
