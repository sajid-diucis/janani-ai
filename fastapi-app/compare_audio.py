
from gtts import gTTS
import io

text = "Ma"
tts = gTTS(text=text, lang="bn", slow=False)
tts.save("gtts_test.mp3")

print("Saved gTTS file.")
