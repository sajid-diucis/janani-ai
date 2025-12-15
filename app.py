import os
import io
import base64
from dotenv import load_dotenv
import streamlit as st
from gtts import gTTS
from openai import OpenAI
import speech_recognition as sr
from PIL import Image
import re

# Load environment variables (for local development)
load_dotenv()

# Helper function to get API keys (works with both local .env and Streamlit Cloud secrets)
def get_secret(key, default=None):
    """Get secret from Streamlit secrets or environment variables"""
    try:
        return st.secrets[key]
    except:
        return os.getenv(key, default)

# Initialize DeepSeek client for chat
client = OpenAI(
    api_key=get_secret("DEEPSEEK_API_KEY"),
    base_url=get_secret("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
)

# Initialize Groq for vision
groq_api_key = get_secret("GROQ_API_KEY")
groq_client = None
if groq_api_key:
    groq_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

# Page configuration
st.set_page_config(
    page_title="জননী এআই - মাতৃস্বাস্থ্য সহায়ক",
    page_icon="🤰",
    layout="wide",
)

# ====================================================================
# Backend Functions
# ====================================================================

def transcribe_audio(audio_bytes):
    """
    Transcribe audio using Google Speech Recognition
    """
    try:
        recognizer = sr.Recognizer()
        audio_data = sr.AudioData(audio_bytes, sample_rate=16000, sample_width=2)
        transcribed_text = recognizer.recognize_google(audio_data, language='bn-BD')
        return transcribed_text
    except sr.UnknownValueError:
        st.warning("দুঃখিত, অডিও বুঝতে পারিনি। আবার চেষ্টা করুন।")
        return "আমার মাথা ব্যথা হচ্ছে"
    except Exception as e:
        st.error(f"ট্রান্সক্রিপশন সমস্যা: {str(e)}")
        return "আমার মাথা ব্যথা হচ্ছে"


def speak_bengali_response(text_to_speak):
    """
    Convert Bengali text to speech - natural conversational tone
    """
    try:
        # Clean text for natural speech
        clean_text = text_to_speak
        # Remove emoji
        clean_text = re.sub(r'[🚨⚠️✅❌🔴📋🍎💊🎤📤💬]', '', clean_text)
        # Remove markdown formatting
        clean_text = re.sub(r'\*\*', '', clean_text)
        clean_text = re.sub(r'\*', '', clean_text)
        clean_text = re.sub(r'#+ ', '', clean_text)
        clean_text = re.sub(r'\[.*?\]\(.*?\)', '', clean_text)
        clean_text = re.sub(r'`', '', clean_text)
        # Normalize whitespace
        clean_text = re.sub(r'\n+', ' ', clean_text)
        clean_text = re.sub(r'^\s*[-]\s*', '', clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r'^\s*\d+\.\s*', '', clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        if len(clean_text) < 5:
            return None
        
        if not clean_text or clean_text.isspace():
            return None
        
        tts = gTTS(text=clean_text, lang='bn', slow=False)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return audio_bytes
    except Exception as e:
        st.error(f"ভয়েস তৈরিতে সমস্যা: {str(e)}")
        return None


def load_guidelines():
    """Load maternal health guidelines"""
    try:
        guidelines_path = os.path.join(os.path.dirname(__file__), "guidelines.txt")
        with open(guidelines_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return """
জরুরি লক্ষণ: রক্তপাত, তীব্র মাথাব্যথা, ঝাপসা দেখা, উচ্চ জ্বর
স্বাস্থ্যকর গর্ভকাল: পুষ্টিকর খাবার, বিশ্রাম, হালকা ব্যায়াম
"""


def janani_ai_response(user_text, guidelines_text, conversation_history=None):
    """
    Conversational midwife-style AI response
    """
    try:
        high_risk_keywords = ['রক্তপাত', 'রক্তস্রাব', 'ঝাপসা', 'তীব্র ব্যথা', 'তীব্র মাথাব্যথা', 'জ্বর', 'অজ্ঞান', 'শ্বাসকষ্ট']
        is_high_risk = any(keyword in user_text for keyword in high_risk_keywords)
        
        system_message = f"""আপনি জননী - একজন অভিজ্ঞ দাই/মিডওয়াইফ। আপনি বাংলায় কথা বলেন, খুব স্বাভাবিক ও মমতাময়ী ভাবে।

কথা বলার ধরন:
- খুব সংক্ষিপ্ত (২-৩ লাইন)
- প্রথমে সমস্যা বুঝতে ছোট প্রশ্ন করুন
- একসাথে একটাই প্রশ্ন করুন
- সাধারণ কথাবার্তার মত, ফর্মাল নয়
- মার্কডাউন ব্যবহার করবেন না
- পয়েন্ট আকারে নয়, গল্পের মত

চিকিৎসা জ্ঞান:
{guidelines_text}

নিয়ম:
- যদি শুধু একটা সমস্যা বলে, তাহলে কতক্ষণ ধরে জিজ্ঞেস করুন
- যদি বিস্তারিত বলে, তাহলে সংক্ষিপ্ত পরামর্শ দিন
- বড় তালিকা দেবেন না
- প্রাকৃতিক কথোপকথন"""
        
        if is_high_risk:
            system_message += "\n\nজরুরি: এই লক্ষণ বিপজ্জনক। সংক্ষেপে জরুরি পরামর্শ দিন। শুরুতে '🚨 মা, এটা জরুরি!' লিখুন।"
        
        messages = [{"role": "system", "content": system_message}]
        
        if conversation_history:
            for msg in conversation_history[-4:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_text})
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.8,
            max_tokens=150,
            top_p=0.9
        )
        
        ai_text = response.choices[0].message.content.strip()
        
        if is_high_risk and not ai_text.startswith("🚨"):
            ai_text = "🚨 মা, এটা জরুরি! " + ai_text
        
        return ai_text
    except Exception as e:
        st.error(f"এআই সমস্যা: {str(e)}")
        if any(keyword in user_text for keyword in ['রক্তপাত', 'ঝাপসা', 'জ্বর']):
            return "🚨 মা, এটা জরুরি! এই লক্ষণ খুব গুরুত্বপূর্ণ। এখনই হাসপাতালে যান।"
        return "বুঝলাম। এটা কতক্ষণ ধরে হচ্ছে?"


def analyze_image_vision(image_file, task_type, analysis_prompt):
    """
    Analyze image using Groq Vision (Llama 4 Scout)
    """
    try:
        if not groq_client:
            return "**ত্রুটি:** Groq এপিআই কী কনফিগার করা হয়নি"
        
        if hasattr(image_file, 'read'):
            image_file.seek(0)
            image_bytes = image_file.read()
        else:
            image_bytes = image_file
        
        # Encode image to base64
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        if task_type == 'Prescription':
            full_prompt = f"""{analysis_prompt}

সংক্ষিপ্ত উত্তর দিন (৩-৪ লাইন):
১. ওষুধের নাম ও ডোজ
২. গর্ভাবস্থায় নিরাপদ কিনা
৩. গুরুত্বপূর্ণ সতর্কতা

বাংলায় উত্তর দিন"""
        else:
            full_prompt = f"""{analysis_prompt}

সংক্ষিপ্ত উত্তর দিন (৩-৪ লাইন):
১. খাবারের নাম
২. ক্যালরি (আনুমানিক)
৩. গর্ভবতী মায়ের জন্য নিরাপদ কিনা
৪. পুষ্টি উপকারিতা

বাংলায় উত্তর দিন"""
        
        # Call Groq Vision API
        response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        if response.choices[0].message.content:
            return response.choices[0].message.content
        return "**দুঃখিত:** ছবি বিশ্লেষণ করা যায়নি"
    except Exception as e:
        return f"**ত্রুটি:** {str(e)}"


# ====================================================================
# UI Implementation - All Bengali
# ====================================================================

st.title("🤰 জননী এআই: আপনার ডিজিটাল মাতৃস্বাস্থ্য সহায়ক")
st.markdown("---")

guidelines = load_guidelines()

tab1, tab2 = st.tabs(["🩺 ডিজিটাল দাই (ভয়েস ও সতর্কতা)", "📋 প্রেসক্রিপশন ও খাবার বিশ্লেষণ"])

# ====================================================================
# Tab 1: Digital Midwife
# ====================================================================
with tab1:
    st.header("🩺 জননী এআই: ভয়েস সঙ্গী")
    st.write("আপনার লক্ষণ, উদ্বেগ বা প্রশ্ন সম্পর্কে স্বাভাবিকভাবে কথা বলুন।")
    
    # Initialize all session state variables
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    
    if "show_alert" not in st.session_state:
        st.session_state.show_alert = False
    
    if "audio_responses" not in st.session_state:
        st.session_state.audio_responses = {}
    
    if "recording_counter" not in st.session_state:
        st.session_state.recording_counter = 0
    
    # Display conversation history FIRST (above recorder)
    st.markdown("---")
    st.subheader("💬 কথোপকথন")
    
    if st.session_state.conversation:
        for idx, msg in enumerate(st.session_state.conversation):
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                # Show audio player for assistant messages
                if msg["role"] == "assistant":
                    audio_key = f"audio_{idx}"
                    if audio_key in st.session_state.audio_responses:
                        # Check if this is the latest message (autoplay only for new)
                        is_latest = idx == len(st.session_state.conversation) - 1
                        if is_latest and st.session_state.get('autoplay_audio', False):
                            # Autoplay for latest response
                            import base64
                            audio_b64 = base64.b64encode(st.session_state.audio_responses[audio_key]).decode()
                            st.markdown(f'<audio autoplay controls src="data:audio/mp3;base64,{audio_b64}"></audio>', unsafe_allow_html=True)
                            st.session_state.autoplay_audio = False
                        else:
                            st.audio(st.session_state.audio_responses[audio_key], format="audio/mp3")
    else:
        st.info("আপনার কথোপকথন এখানে দেখা যাবে। নিচে রেকর্ড করুন।")
    
    # Voice input section - AFTER conversation history
    st.markdown("---")
    st.subheader("🎤 নতুন বার্তা রেকর্ড করুন")
    
    # Dynamic key forces fresh recorder after each submission
    audio_file = st.audio_input(
        "আপনার ভয়েস মেসেজ রেকর্ড করুন", 
        key=f"audio_input_{st.session_state.recording_counter}"
    )
    
    if audio_file:
        # Auto-process immediately when audio is recorded
        with st.spinner("🔄 প্রক্রিয়া করা হচ্ছে..."):
            try:
                audio_bytes = audio_file.read()
                transcribed_text = transcribe_audio(audio_bytes)
                
                # Get AI response
                ai_response = janani_ai_response(transcribed_text, guidelines, st.session_state.conversation)
                
                # Add user message
                st.session_state.conversation.append({"role": "user", "content": transcribed_text})
                
                # Add assistant message
                st.session_state.conversation.append({"role": "assistant", "content": ai_response})
                
                # Check for alert
                if ai_response.startswith("🚨"):
                    st.session_state.show_alert = True
                
                # Generate and store audio for this response
                audio_response = speak_bengali_response(ai_response)
                if audio_response:
                    audio_key = f"audio_{len(st.session_state.conversation)-1}"
                    st.session_state.audio_responses[audio_key] = audio_response.getvalue()
                    st.session_state.autoplay_audio = True  # Enable autoplay for new audio
                
                # Increment counter to reset the audio input widget
                st.session_state.recording_counter += 1
                
                st.rerun()
            except Exception as e:
                st.error(f"সমস্যা হয়েছে: {str(e)}")
    
    # Early warning alert
    if st.session_state.show_alert:
        st.markdown("---")
        st.markdown("""
            <div style="background-color: #ff4444; color: white; padding: 20px; border-radius: 10px; border: 3px solid #cc0000; font-weight: bold;">
                <h2 style="color: white; margin: 0;">🚨 লাল সতর্কতা: জরুরি চিকিৎসা প্রয়োজন</h2>
                <p style="font-size: 18px; margin-top: 10px;">
                    আপনার লক্ষণগুলো গুরুতর সমস্যার ইঙ্গিত দেয়।
                    অনুগ্রহ করে অবিলম্বে হাসপাতালে যান।
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📞 জরুরি সেবা কল করুন", type="primary"):
                st.warning("জরুরি যোগাযোগ ফিচার শীঘ্রই আসছে")
        with col_b:
            if st.button("❌ সতর্কতা বন্ধ করুন"):
                st.session_state.show_alert = False
                st.rerun()

# ====================================================================
# Tab 2: Vision Analysis
# ====================================================================
with tab2:
    st.header("📋 ছবি ও ডকুমেন্ট বিশ্লেষণ")
    col1, col2 = st.columns(2)
    
    # Initialize session state for prescription
    if "prescription_processed" not in st.session_state:
        st.session_state.prescription_processed = None
    
    with col1:
        st.subheader("💊 প্রেসক্রিপশন বিশ্লেষণ")
        prescription_file = st.file_uploader("প্রেসক্রিপশন আপলোড করুন", type=['jpg', 'jpeg', 'png'], key="prescription_uploader")
        
        if prescription_file:
            # Check if this is a new file
            file_id = f"{prescription_file.name}_{prescription_file.size}"
            
            if st.session_state.prescription_processed != file_id:
                st.image(prescription_file, caption="আপলোড করা প্রেসক্রিপশন", width=400)
                
                # Auto-process immediately
                with st.spinner("🔄 বিশ্লেষণ করা হচ্ছে..."):
                    try:
                        prompt = "এই প্রেসক্রিপশন থেকে ওষুধের নাম, ডোজ এবং গর্ভাবস্থায় নিরাপত্তা চিহ্নিত করুন"
                        result = analyze_image_vision(prescription_file, 'Prescription', prompt)
                        st.success("✅ বিশ্লেষণ সম্পন্ন!")
                        st.markdown(result)
                        
                        # Auto-play audio
                        audio_response = speak_bengali_response(result)
                        if audio_response:
                            audio_b64 = base64.b64encode(audio_response.getvalue()).decode()
                            st.markdown(f'<audio autoplay controls src="data:audio/mp3;base64,{audio_b64}"></audio>', unsafe_allow_html=True)
                        
                        st.session_state.prescription_processed = file_id
                    except Exception as e:
                        st.error(f"সমস্যা হয়েছে: {str(e)}")
            else:
                st.image(prescription_file, caption="আপলোড করা প্রেসক্রিপশন", width=400)
                st.info("নতুন প্রেসক্রিপশন আপলোড করুন বিশ্লেষণের জন্য")
        else:
            st.session_state.prescription_processed = None
            st.info("বিশ্লেষণের জন্য প্রেসক্রিপশন ছবি আপলোড করুন")
    
    # Initialize session state for food
    if "food_processed" not in st.session_state:
        st.session_state.food_processed = None
    
    with col2:
        st.subheader("🍎 খাবার বিশ্লেষণ")
        food_tab1, food_tab2 = st.tabs(["📷 ক্যামেরা", "📁 আপলোড"])
        
        food_image = None
        with food_tab1:
            camera_food = st.camera_input("খাবারের ছবি তুলুন", key="food_camera")
            if camera_food:
                food_image = camera_food
        
        with food_tab2:
            uploaded_food = st.file_uploader("খাবারের ছবি আপলোড করুন", type=['jpg', 'jpeg', 'png'], key="food_uploader")
            if uploaded_food:
                food_image = uploaded_food
        
        if food_image:
            # Create unique ID for the image
            file_id = f"food_{food_image.size}_{id(food_image)}"
            
            if st.session_state.food_processed != file_id:
                st.image(food_image, caption="খাবারের ছবি", width=400)
                
                # Auto-process immediately
                with st.spinner("🔄 বিশ্লেষণ করা হচ্ছে..."):
                    try:
                        prompt = "এই খাবার চিহ্নিত করুন এবং ক্যালরি, গর্ভবতী মায়ের জন্য নিরাপত্তা বিশ্লেষণ করুন"
                        result = analyze_image_vision(food_image, 'Diet', prompt)
                        
                        st.success("✅ বিশ্লেষণ সম্পন্ন!")
                        st.markdown(result)
                        
                        # Auto-play audio
                        audio_response = speak_bengali_response(result)
                        if audio_response:
                            audio_b64 = base64.b64encode(audio_response.getvalue()).decode()
                            st.markdown(f'<audio autoplay controls src="data:audio/mp3;base64,{audio_b64}"></audio>', unsafe_allow_html=True)
                        
                        st.session_state.food_processed = file_id
                    except Exception as e:
                        st.error(f"সমস্যা হয়েছে: {str(e)}")
            else:
                st.image(food_image, caption="খাবারের ছবি", width=400)
                st.info("নতুন খাবারের ছবি তুলুন বা আপলোড করুন")
        else:
            st.session_state.food_processed = None
            st.info("বিশ্লেষণের জন্য খাবারের ছবি তুলুন বা আপলোড করুন")

st.markdown("---")
st.caption("🔒 আপনার তথ্য সুরক্ষিত ও গোপনীয়")
