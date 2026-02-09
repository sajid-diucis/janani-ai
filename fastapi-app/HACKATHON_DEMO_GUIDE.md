# 🚀 Janani Hackathon Demo Guide

## Quick Start

### Switch Demo Mode
```bash
cd c:\Users\User\Documents\buildathon\Janani\fastapi-app
python switch_mode.py
```

### Restart Server (Required After Mode Change)
```bash
python main.py
```

---

## 3 Demo Modes

| Mode | Response Time | Best For |
|------|--------------|----------|
| **SPEED** | 3-5s | 2-minute demo (DEFAULT) |
| **BALANCED** | 8-10s | Mixed presentations |
| **FULL** | 15-20s | Q&A feature showcase |

---

## Demo Strategy

### Phase 1: Initial Demo (2 minutes) - SPEED MODE

**What judges see:**
- ✅ Emergency detection: 2-3s
- ✅ Voice triage: 3-4s
- ✅ AR dashboard: Instant
- ✅ Food safety: 4-5s

**Judges think:** "Wow, this is FAST and works!"

### Phase 2: Q&A (5-10 minutes) - FULL MODE

**When judges ask:** "What makes this special?"

**You say:** "Let me show you our advanced features..."

**Live switch:**
1. Stop server (Ctrl+C)
2. Run: `python switch_mode.py` → Select 3
3. Restart: `python main.py`

---

## Feature Demos

### Dialect Translation
```
Input: "আঁর মাডা বিষ লাগতাছে" (Noakhali dialect)
Shows: Translation layer (8-10s)
```

### Empathetic AI
```
Input: "আমার মন খারাপ লাগছে" (I feel sad)
Shows: Emotional support response (12-15s)
```

### WHO Safety Guard
```
Input: "আমি কি aspirin খেতে পারি?" (Can I take aspirin?)
Shows: WHO guideline validation (5-6s)
```

### Memory Feature
```
Input 1: "আমার ডায়াবেটিস আছে" (I have diabetes)
Input 2: "আমি কি মিষ্টি খেতে পারি?" (Can I eat sweets?)
Shows: Remembers context (8-10s)
```

---

## Emergency Demo Commands

Test these in the chat:
- **Emergency:** "রক্তপাত হচ্ছে" (Bleeding) → AR Dashboard
- **Triage:** "মাথা ব্যথা আর চোখে ঝাপসা" (Headache + blurred vision)
- **Food:** "আমি কি পেঁপে খেতে পারি?" (Can I eat papaya?)

---

## Key Talking Points

### For Speed:
> "Our system responds in 3-5 seconds - critical for emergencies where every second counts."

### For Features:
> "We have 7 advanced features: dialect translation, hybrid AI, WHO validation, conversation memory, and more."

### For Impact:
> "In Bangladesh, 1 woman dies every 2 hours during pregnancy. Janani AI can save them with instant detection and offline AR guidance."

---

## URLs to Open

- **Main App:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **AR Dashboard:** http://localhost:8000/ar-dashboard
