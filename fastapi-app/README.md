# 🚀 Janani AI FastAPI - Setup & Run Guide

## ✅ Migration Complete! 

Your Streamlit app has been successfully migrated to FastAPI with a modern web frontend.

## 📁 New Project Structure
```
fastapi-app/
├── main.py              # FastAPI application entry point
├── config.py           # Configuration settings
├── requirements.txt    # Dependencies
├── .env                # Environment variables (configure this!)
├── guidelines.txt      # Health guidelines
├── routers/            # API endpoints
│   ├── voice.py        # Voice/speech APIs
│   ├── chat.py         # Chat/AI APIs  
│   ├── vision.py       # Image analysis APIs
│   └── emergency.py    # Emergency detection APIs
├── services/           # Business logic
│   ├── ai_service.py       # DeepSeek AI integration
│   ├── speech_service.py   # Speech processing
│   ├── vision_service.py   # Image analysis
│   └── emergency_service.py # Emergency detection
├── models/             # API data models
├── templates/          # Web frontend
│   └── index.html      # Main web interface
└── static/            # Static files (CSS, JS, images)
```

## 🔧 Setup Steps

### 1. Configure API Keys
Edit `.env` file and add your API keys:
```env
DEEPSEEK_API_KEY=your_deepseek_key
GROQ_API_KEY=your_groq_api_key
```

### 2. Install Dependencies (Already Done)
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python main.py
```

The app will be available at:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🌟 New Features

### 🔗 **Pure API Backend**
- RESTful APIs for all functionality
- Perfect for mobile app integration
- OpenAPI/Swagger documentation
- JSON responses

### 🌐 **Modern Web Frontend**
- Same features as Streamlit app
- Better UI/UX with animations
- Responsive design (mobile-friendly)
- Real-time voice recording
- Drag & drop file upload

### 📱 **Mobile-Ready**
- APIs can be called from mobile apps
- Audio file upload/processing
- Image analysis endpoints
- Real-time chat functionality

## 📚 API Endpoints

### Voice & Chat APIs
- `POST /api/voice/transcribe` - Convert audio to text
- `POST /api/voice/speak` - Convert text to speech
- `POST /api/chat/message` - Send message to AI
- `GET /api/chat/history/{conversation_id}` - Get chat history

### Image Analysis APIs  
- `POST /api/vision/prescription/analyze` - Analyze prescription
- `POST /api/vision/food/analyze` - Analyze food safety

### Emergency APIs
- `POST /api/emergency/check` - Check for emergency keywords
- `GET /api/emergency/keywords` - Get emergency keyword list

### Utility APIs
- `GET /health` - Health check
- `GET /` - Web interface

## 🎯 How to Use

### Web Interface (Same as Streamlit)
1. Open http://localhost:8000 in browser
2. Use the 3 tabs:
   - **🎤 ভয়েস চ্যাট**: Voice chat & text messaging
   - **💊 প্রেসক্রিপশন**: Upload prescription images  
   - **🍎 খাদ্য বিশ্লেষণ**: Upload food images

### API Integration (For Developers)
```javascript
// Example: Voice transcription
const formData = new FormData();
formData.append('audio', audioFile);

const response = await fetch('/api/voice/transcribe', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(result.transcription); // Bengali text
```

## 🚀 Deployment Options

### Local Development
```bash
python main.py  # Runs on http://localhost:8000
```

### Production Deployment
```bash
# With Gunicorn (Linux/Mac)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# With Uvicorn directly  
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment
- **Railway**: Connect GitHub repo, auto-deploys
- **Render**: Similar to Heroku, easy deployment
- **Google Cloud Run**: Containerized deployment
- **AWS Lambda**: Serverless with Mangum adapter

## 🔄 Migration Benefits

### ✅ **What You Gained**
- **Better Performance**: Async processing, faster responses
- **API-First**: Can build mobile apps, integrate with other services
- **Production Ready**: Proper error handling, logging, monitoring
- **Scalability**: Handle multiple concurrent users
- **Modern Frontend**: Better UI/UX, responsive design
- **Developer Friendly**: OpenAPI docs, clear separation of concerns

### 🏃‍♂️ **What Stays the Same**
- **All Features**: Voice chat, prescription analysis, food analysis
- **Bengali Language**: Full Bengali support maintained
- **Emergency Detection**: Same keyword-based emergency alerts
- **AI Integration**: Same DeepSeek and Groq APIs
- **User Experience**: Similar workflow for end users

## 🐛 Troubleshooting

### Common Issues

**1. API Key Errors**
```
Error: The api_key client option must be set
```
Solution: Add your API keys to `.env` file

**2. Import Errors**
```
ModuleNotFoundError: No module named 'fastapi'
```
Solution: `pip install -r requirements.txt`

**3. Audio Upload Issues**
- Ensure audio files are in supported formats (WAV, MP3, M4A)
- Check file size (max 10MB)
- Enable microphone permissions in browser

**4. Image Upload Issues**
- Supported formats: JPG, PNG, WEBP
- Maximum size: 10MB
- Check API keys for Groq vision service

## 🎉 Next Steps

1. **Add Your API Keys** to `.env` file
2. **Run the App** with `python main.py`
3. **Test All Features** in the web interface
4. **Check API Documentation** at `/docs`
5. **Build Mobile App** using the APIs (optional)

## 📞 Support

If you encounter issues:
1. Check the terminal logs for error messages
2. Verify API keys are correctly set
3. Ensure all dependencies are installed
4. Check file permissions and formats

---

**🎯 Your FastAPI migration is complete! Enjoy the improved performance and new capabilities!** 🚀