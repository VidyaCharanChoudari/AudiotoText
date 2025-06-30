import whisper
import pyaudio
import wave
import tempfile
import os

# Initialize Whisper model
def load_model(model_name="base"):
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print("Model loaded successfully.")
    return model

# Record audio and save it to a .wav file
def record_audio(filename, duration=5):
    print("Recording audio...")
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    rate = 44100  # Record at 44100 samples per second

    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []

    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data as a .wav file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    print(f"Recording saved to {filename}")

# Upload and verify an existing audio file
def upload_audio(filename):
    if not os.path.exists(filename):
        print(f"❌ File not found at path: {filename}")
        return None
    print(f"✅ Audio file '{filename}' loaded successfully.")
    return filename

# Translate audio using the Whisper model
def translate_audio(model, audio_path):
    print("Translating audio to English...")
    try:
        transcription = model.transcribe(audio_path, task="translate")
        transcribed_text = transcription["text"]
        print("✅ Translation complete.")
        return transcribed_text
    except Exception as e:
        print(f"❌ Error during translation: {e}")
        return None

# Save translation to a text file
def save_translation(text, filename="translation.txt"):
    with open(filename, "w") as f:
        f.write(text)
    print(f"📁 Translation saved to {filename}")

# Main function to select options and perform tasks
def main():
    model_name = input("Enter the Whisper model size to load (e.g., tiny, base, small, medium, large): ")
    model = load_model(model_name)
    
    print("\nChoose an option:")
    print("1. 🎙️  Record audio")
    print("2. 📂 Upload existing audio file")
    option = input("Enter option (1 or 2): ")

    audio_file_path = None

    if option == "1":
        try:
            duration = int(input("Enter recording duration in seconds: "))
        except ValueError:
            print("❌ Invalid duration. Exiting.")
            return
        audio_file_path = tempfile.mktemp(suffix=".wav")
        record_audio(audio_file_path, duration)

    elif option == "2":
        print("⚠️  Make sure the file path is correct and includes the extension (e.g., sample.wav or sample.mp3).")
        user_path = input("Enter the full path or filename of the audio file to upload: ").strip()
        audio_file_path = upload_audio(user_path)

    else:
        print("❌ Invalid option selected.")
        return

    # Proceed only if valid file was loaded or recorded
    if audio_file_path:
        translated_text = translate_audio(model, audio_file_path)
        if translated_text:
            print("\n📝 Translated Text:\n", translated_text)

            save_option = input("\nDo you want to save the translation to a text file? (y/n): ")
            if save_option.lower() == "y":
                save_translation(translated_text)
        else:
            print("❌ Translation failed.")
    else:
        print("❌ No valid audio file provided.")

    # Clean up temporary file if recorded
    if option == "1" and audio_file_path and os.path.exists(audio_file_path):
        os.remove(audio_file_path)
        print(f"🧹 Temporary file deleted: {audio_file_path}")

# Run the main function

if __name__ == "__main__":
    main()
