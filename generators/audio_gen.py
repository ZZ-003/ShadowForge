from gtts import gTTS
import os
import pyttsx3
import math
import asyncio
import socket
import subprocess
import wave
from array import array

class AudioGenerator:
    def __init__(self, lang='en-us', slow=False):
        self.lang = lang
        self.slow = slow

    def generate_audio(self, text, output_path, secret=None, secret_placeholder="SECRET_HERE"):
        """
        Generates an audio file from text.
        Tries gTTS first (online), falls back to pyttsx3 (offline) if network fails.
        """
        text_value = text if isinstance(text, str) else str(text)

        if secret and secret_placeholder in text_value:
            final_text = text_value.replace(secret_placeholder, secret)
        else:
            final_text = text_value

        # 1) Google Cloud TTS (best quality if credentials are configured)
        cloud_path = self._try_google_cloud_tts(final_text, output_path)
        if cloud_path:
            return cloud_path

        # 2) gTTS (Google Translate)
        gtts_path = self._try_gtts(final_text, output_path)
        if gtts_path:
            return gtts_path

        # 3) Edge TTS online fallback (often works when Google endpoints fail)
        edge_path = self._try_edge_tts(final_text, output_path)
        if edge_path:
            return edge_path

        # 4) Local offline TTS
        offline_path = self._try_offline_tts(final_text, output_path)
        if offline_path:
            return offline_path

        # 5) Final fallback: tone WAV + sidecar transcript
        try:
            fallback_path = output_path
            if fallback_path.endswith('.mp3'):
                fallback_path = fallback_path.replace('.mp3', '.wav')
            self._generate_tone_wav(fallback_path, final_text)
            transcript_path = f"{os.path.splitext(fallback_path)[0]}.txt"
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            print(f"Falling back to tone WAV: {fallback_path}")
            print(f"Saved transcript: {transcript_path}")
            return fallback_path
        except Exception as e:
            print(f"Error generating final fallback audio: {e}")
            return None

    def _try_google_cloud_tts(self, text, output_path):
        try:
            from google.cloud import texttospeech
        except Exception:
            return None

        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return None

        try:
            client = texttospeech.TextToSpeechClient()
            input_text = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(language_code="en-US")
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            response = client.synthesize_speech(
                input=input_text,
                voice=voice,
                audio_config=audio_config,
            )
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            return output_path
        except Exception as e:
            print(f"Warning: Google Cloud TTS failed: {e}")
            return None

    def _try_gtts(self, text, output_path):
        try:
            socket.create_connection(("translate.google.com", 80), timeout=2)
            tts = gTTS(text=text, lang=self.lang, slow=self.slow)
            tts.save(output_path)
            return output_path
        except Exception as e:
            print(f"Warning: gTTS failed: {e}")
            return None

    def _try_edge_tts(self, text, output_path):
        try:
            import edge_tts
        except Exception:
            return None

        try:
            socket.create_connection(("api.msedgeservices.com", 443), timeout=2)
            communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
            asyncio.run(communicate.save(output_path))
            return output_path
        except Exception as e:
            print(f"Warning: Edge TTS failed: {e}")
            return None

    def _try_offline_tts(self, text, output_path):
        try:
            fallback_path = output_path
            if output_path.endswith('.mp3'):
                fallback_path = output_path.replace('.mp3', '.wav')
                print(f"Changing output format to WAV for offline TTS: {fallback_path}")

            try:
                subprocess.run(['espeak-ng', '-w', fallback_path, text], check=True)
                return fallback_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.save_to_file(text, fallback_path)
                engine.runAndWait()
                if getattr(engine, '_inLoop', False):
                    engine.endLoop()
                return fallback_path
        except Exception as e:
            print(f"Error generating offline audio: {e}")
            return None

    def _generate_tone_wav(self, output_path, text):
        sample_rate = 16000
        channels = 1
        sample_width = 2  # 16-bit
        max_amp = 32767

        # Keep duration bounded but proportional to content length.
        duration_sec = max(2.0, min(15.0, len(text) / 20.0))
        total_samples = int(sample_rate * duration_sec)

        with wave.open(output_path, 'w') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)

            samples = array('h')
            for i in range(total_samples):
                t = i / sample_rate
                # Soft two-tone blend to mimic notification-like audio.
                tone = 0.5 * math.sin(2 * math.pi * 440 * t) + 0.3 * math.sin(2 * math.pi * 660 * t)
                # Fade in/out to avoid clicks.
                fade = 1.0
                if t < 0.05:
                    fade = t / 0.05
                elif duration_sec - t < 0.05:
                    fade = max(0.0, (duration_sec - t) / 0.05)
                value = int(max_amp * 0.18 * tone * fade)
                samples.append(value)

            wav_file.writeframes(samples.tobytes())
