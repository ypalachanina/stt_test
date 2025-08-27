import azure.cognitiveservices.speech as speechsdk
import tempfile
import os
import io
from pydub import AudioSegment
from google.cloud import speech
from google.api_core.client_options import ClientOptions


def process_audio(audio):
    audio_bytes = audio.export().read()

    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    wav_buffer = io.BytesIO()
    audio_segment.export(wav_buffer, format="wav")
    wav_bytes = wav_buffer.getvalue()

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
        tmp_file.write(wav_bytes)
        tmp_file_path = tmp_file.name

    return wav_bytes, tmp_file_path


def azure_stt(tmp_file_path, language_code, api_key):
    speech_config = speechsdk.SpeechConfig(subscription=api_key, region="westeurope")
    # auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=languages)
    speech_config.speech_recognition_language = language_code
    audio_config = speechsdk.AudioConfig(filename=tmp_file_path)

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config,
        # auto_detect_source_language_config=auto_detect_source_language_config
    )

    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        result_text = result.text
        # detected_language = result.properties.get(speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult)
        # result_text += f"\n\n[Detected language: {detected_language}]"
    else:
        cancellation_details = result.cancellation_details
        result_text = f"Error: {result.reason}"
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            result_text += f"\nError details: {cancellation_details.error_details}"

    del speech_recognizer
    del audio_config
    os.remove(tmp_file_path)

    return result_text


def google_stt(wav_bytes, language, api_key):
    client_options = ClientOptions(api_key=api_key)
    client = speech.SpeechClient(client_options=client_options)
    audio = speech.RecognitionAudio(content=wav_bytes)

    recognition_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language,
        enable_automatic_punctuation=True,
        model='default'
    )

    result = client.recognize(config=recognition_config, audio=audio)
    if result.results:
        best_alternative = result.results[0].alternatives[0]
        result_text = best_alternative.transcript
        # detected_language = response.results[0].language_code
        # result_text += f"\n\n[Detected language: {detected_language}]"
    else:
        result_text = "Error: No speech recognized"
    return result_text
