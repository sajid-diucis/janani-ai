import fs from 'fs';
import path from 'path';
import followRedirects from 'follow-redirects';
const { https } = followRedirects;

// The folder where we want the model to live
// NOTE: process.cwd() should be c:\Users\User\Documents\buildathon\Janani\frontend
const MODEL_DIR = path.join(process.cwd(), 'public', 'models', 'Xenova', 'all-MiniLM-L6-v2');

// The files we need from Hugging Face
const FILES = [
    'config.json',
    'tokenizer.json',
    'tokenizer_config.json',
    'onnx/model_quantized.onnx',
    'special_tokens_map.json'
];

// Fixed URL: removed markdown characters
const BASE_URL = 'https://huggingface.co/Xenova/all-MiniLM-L6-v2/resolve/main/';

// Ensure directory exists
if (!fs.existsSync(MODEL_DIR)) {
    fs.mkdirSync(MODEL_DIR, { recursive: true });
    console.log(`📂 Created directory: ${MODEL_DIR}`);
}

// Ensure onnx subdirectory exists
const ONNX_DIR = path.join(MODEL_DIR, 'onnx');
if (!fs.existsSync(ONNX_DIR)) {
    fs.mkdirSync(ONNX_DIR, { recursive: true });
    console.log(`📂 Created directory: ${ONNX_DIR}`);
}

// Helper function to download a file
const downloadFile = (filename) => {
    const fileUrl = BASE_URL + filename;
    const filePath = path.join(MODEL_DIR, filename);
    const fileStream = fs.createWriteStream(filePath);

    console.log(`⬇️  Downloading ${filename}...`);

    https.get(fileUrl, (response) => {
        if (response.statusCode !== 200) {
            console.error(`❌ Failed to download ${filename}: Status ${response.statusCode}`);
            return;
        }
        response.pipe(fileStream);

        fileStream.on('finish', () => {
            fileStream.close();
            console.log(`✅ ${filename} saved.`);
        });
    }).on('error', (err) => {
        fs.unlink(filename);
        console.error(`❌ Error downloading ${filename}: ${err.message}`);
    });
};

// Helper function to download a file from a direct URL
const downloadUrl = (url, destPath) => {
    const fileStream = fs.createWriteStream(destPath);
    console.log(`⬇️  Downloading ${path.basename(destPath)}...`);

    https.get(url, (response) => {
        if (response.statusCode !== 200) {
            console.error(`❌ Failed to download ${url}: Status ${response.statusCode}`);
            return;
        }
        response.pipe(fileStream);

        fileStream.on('finish', () => {
            fileStream.close();
            console.log(`✅ ${path.basename(destPath)} saved.`);
        });
    }).on('error', (err) => {
        fs.unlink(destPath);
        console.error(`❌ Error downloading ${path.basename(destPath)}: ${err.message}`);
    });
};

// Start downloading Model Files
FILES.forEach(file => downloadFile(file));

// --- NEW: Download WASM Binaries for Offline Runtime ---
const WASM_DIR = path.join(process.cwd(), 'public', 'wasm');
if (!fs.existsSync(WASM_DIR)) {
    fs.mkdirSync(WASM_DIR, { recursive: true });
    console.log(`📂 Created directory: ${WASM_DIR}`);
}

const WASM_FILES = [
    'ort-wasm.wasm',
    'ort-wasm-simd.wasm',
    'ort-wasm-threaded.wasm'
];
const WASM_BASE_URL = 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/dist/';

WASM_FILES.forEach(file => {
    const url = WASM_BASE_URL + file;
    const dest = path.join(WASM_DIR, file);
    if (!fs.existsSync(dest)) {
        downloadUrl(url, dest);
    } else {
        console.log(`⏭️  Skipped ${file} (exists)`);
    }
});

// --- NEW: Download JS Libraries for Offline Access ---
const LIBS_DIR = path.join(process.cwd(), 'public', 'libs');
if (!fs.existsSync(LIBS_DIR)) {
    fs.mkdirSync(LIBS_DIR, { recursive: true });
    console.log(`📂 Created directory: ${LIBS_DIR}`);
}

const LIB_FILES = [
    { url: 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2/dist/transformers.min.js', name: 'transformers.min.js' },
    { url: 'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.14.0/dist/ort.min.js', name: 'ort.min.js' }
];

LIB_FILES.forEach(lib => {
    const dest = path.join(LIBS_DIR, lib.name);
    if (!fs.existsSync(dest)) {
        downloadUrl(lib.url, dest);
    } else {
        console.log(`⏭️  Skipped ${lib.name} (exists)`);
    }
});
