# 🤰 জননী এআই (Janani AI)

**বাংলায় মাতৃস্বাস্থ্য সহায়ক | Bengali Maternal Health Assistant**

## ✨ ফিচার

- 🎤 **ভয়েস চ্যাটবট** - বাংলায় কথা বলুন, বাংলায় উত্তর পান
- 💊 **প্রেসক্রিপশন বিশ্লেষণ** - ওষুধের নিরাপত্তা যাচাই
- 🍎 **খাবার বিশ্লেষণ** - ক্যালরি ও পুষ্টি তথ্য
- 🚨 **জরুরি সতর্কতা** - বিপদজনক লক্ষণ শনাক্তকরণ

## 🛠️ টেকনোলজি

- **Frontend:** Streamlit
- **Chat AI:** DeepSeek
- **Vision AI:** Groq (Llama 4 Scout)
- **Speech-to-Text:** Google Speech Recognition
- **Text-to-Speech:** gTTS

## 🚀 লোকাল সেটআপ

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/janani-ai.git
cd janani-ai

# Install
pip install -r requirements.txt

# Run
streamlit run app.py
```

## 🔑 API Keys

`.streamlit/secrets.toml` ফাইলে:
```toml
DEEPSEEK_API_KEY = "your-key"
GROQ_API_KEY = "your-key"
```

## 📝 License

MIT License
