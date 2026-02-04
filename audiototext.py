import streamlit as st
import whisper
import tempfile
import os
import logging
from gtts import gTTS

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define the folder path for saving audio files
SAVE_DIR = os.path.join(os.getcwd(), "project_audio_files")

os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize session state variables
if 'model' not in st.session_state:
    st.session_state.model = None
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'uploaded_audio_path' not in st.session_state:
    st.session_state.uploaded_audio_path = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# Function to load the Whisper model
def load_model(model_name):
    try:
        st.session_state.model = whisper.load_model(model_name)
        st.session_state.model_loaded = True
        st.sidebar.success(f"Whisper Model '{model_name}' Loaded")
    except Exception as e:
        st.sidebar.error(f"Error loading model: {e}")
        logging.error(f"Model loading error: {e}")

# Function to save uploaded audio
def save_uploaded_audio(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(uploaded_file.read())
            st.session_state.uploaded_audio_path = temp_audio_file.name
        return st.session_state.uploaded_audio_path
    except Exception as e:
        st.sidebar.error(f"Error saving audio file: {e}")
        logging.error(f"Audio save error: {e}")

# Function to map detected language codes to full language names
def language_code_to_name(code):
    code_map = {
        "en": "English", "hi": "Hindi", "fr": "French", "te": "Telugu", "es": "Spanish",
        "de": "German", "ja": "Japanese", "ta": "Tamil", "bn": "Bengali", "mr": "Marathi",
        "gu": "Gujarati", "pa": "Punjabi", "ml": "Malayalam", "or": "Odia", "ur": "Urdu", 
        "pt": "Portuguese"
    }
    return code_map.get(code, "Unknown Language")  # Default to Unknown Language

# Main Content: Welcome Image, Title, and Instructions
st.markdown("""
    <style>
        body { background-color: #1c1c1c; }
        .futuristic-box { background: linear-gradient(to right, #0f0c29, #302b63, #24243e); padding: 20px; border-radius: 15px; box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.4); color: #00ffff; font-family: 'Courier New', Courier, monospace; }
        h1, h2, h3 { color: #00ffff; }
    </style>
    <div style="text-align: center;">
        <img src="https://cdn.prod.website-files.com/5fac161927bf86485ba43fd0/64705e36d6c173f75626cf6b_Blog-Cover-2022_02_How-to-Transcribe-Audio-to-Text-(Automatically-_-For-Free).jpeg" alt="welcome image" style="width: 100%; max-width: 600px; border-radius: 15px;">
        <h1 style="font-size: 50px; font-family: 'Orbitron', sans-serif; text-shadow: 2px 2px 10px #000000; margin-top: 10px;">
            Convert All Languages to English
        </h1>
        <p style="font-size: 18px; color: #00ffff;">
            Heyyy, upload your audio, get it in the form of text.
        </p>
        <img src="https://media.tenor.com/J8LIZC2OVOoAAAAj/rob%C3%B4.gif" alt="robot gif" style="width: 200px; margin-top: 20px;">
    </div>
""", unsafe_allow_html=True)

# Sidebar: Model selection and audio upload
st.sidebar.header("Model Selection")
model_options = ["tiny", "base", "small", "medium", "large"]
model_name = st.sidebar.selectbox("Select Whisper Model", model_options)

# Load model button
if st.sidebar.button("Load Model"):
    load_model(model_name)

# Sidebar for uploading pre-recorded audio
st.sidebar.header("Upload Audio")
audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a"])

if audio_file:
    uploaded_audio_path = save_uploaded_audio(audio_file)
    st.sidebar.success("Audio file uploaded and saved.")

# Play original audio playback
if st.session_state.uploaded_audio_path:
    st.sidebar.audio(st.session_state.uploaded_audio_path)

# Translation section
if st.session_state.model_loaded and st.session_state.uploaded_audio_path:
    st.sidebar.header("Translate Audio")
    if st.sidebar.button("Translate Audio"):
        st.session_state.is_loading = True
        with st.spinner('Translating audio...'):  # Add spinner for loading
            try:
                # Transcribe and detect language
                result = st.session_state.model.transcribe(st.session_state.uploaded_audio_path, task="translate")
                transcribed_text = result["text"]
                detected_language_code = result["language"]

                # Log the transcribed text for debugging
                logging.debug(f"Transcribed Text: {transcribed_text}")

                # Convert language code to full name
                detected_language_name = language_code_to_name(detected_language_code)

                # Display detected language and translated text
                st.sidebar.success("Translation complete")
                st.markdown(f"""<div class="futuristic-box"><h3>Translated Text:</h3><p>{transcribed_text}</p></div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class="futuristic-box"><h3>Detected Language:</h3><p>{detected_language_name}</p></div>""", unsafe_allow_html=True)

                # Convert the translated text to English speech and save it
                output_audio_path = os.path.join(SAVE_DIR, "translated_audio.mp3")
                tts = gTTS(text=transcribed_text, lang="en")
                tts.save(output_audio_path)

                # Display the title above the AI voice player
                st.markdown('<h2 style="text-align: center; font-family: \'Orbitron\', sans-serif; color: #00ffff;">Echo of AI: Hear It in English</h2>', unsafe_allow_html=True)

                # Play the translated audio in the Streamlit app
                with open(output_audio_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3")

                # Download options
                st.sidebar.download_button(
                    label="Download Translated Audio",
                    data=open(output_audio_path, "rb").read(),
                    file_name="translated_audio.mp3",
                    mime="audio/mp3"
                )

                # Download translated text option
                st.sidebar.download_button(
                    label="Download Translated Text",
                    data=transcribed_text,
                    file_name="translated_text.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.sidebar.error(f"Error translating audio: {e}")
                logging.error(f"Translation error: {e}")
            finally:
                st.session_state.is_loading = False