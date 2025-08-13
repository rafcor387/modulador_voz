import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv()
cfg  = speechsdk.SpeechConfig(subscription=os.getenv("SPEECH_KEY"), region=os.getenv("SPEECH_REGION"))
synth= speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=None)
voices = synth.get_voices_async().get()
es = [v for v in voices.voices if v.locale.startswith("es")]
for v in es:
    print(v.name, "-", v.locale)
