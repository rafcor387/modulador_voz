import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv() 

KEY    = os.getenv("SPEECH_KEY")
REGION = os.getenv("SPEECH_REGION")
if not KEY or not REGION:
    raise RuntimeError("Falta SPEECH_KEY o SPEECH_REGION en .env")

speech_config = speechsdk.SpeechConfig(subscription=KEY, region=REGION)
speech_config.set_speech_synthesis_output_format(
    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3
)

texto = " Hola, soy tu asistente. Voy a hablar con voz natural y modulada."

ssml = f"""
<speak version="1.0" xml:lang="es-MX" xmlns:mstts="https://www.w3.org/2001/mstts">
  <mstts:backgroundaudio src="https://.../ambiente.mp3" volume="0.2" fadein="500ms" fadeout="800ms"/>
  <voice name="es-MX-DaliaNeural" effect="eq_car">
    <mstts:silence type="Sentenceboundary" value="200ms"/>
    <mstts:express-as style="cheerful" styledegree="1.2" role="YoungAdultFemale">
      <prosody rate="+4%" pitch="+1st" volume="+10%">
        ¡Hola! <break time="250ms"/>
        Vamos a empezar la demo con buena energía.
        si tienes dudas pregunta
      </prosody>
    </mstts:express-as>
  </voice>
</speak>

""".strip()

synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
result = synthesizer.speak_ssml_async(ssml).get()

if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
    detail = result.cancellation_details.reason if result.cancellation_details else "desconocido"
    raise RuntimeError(f"Azure TTS error: {detail}")

with open("respuesta.mp3", "wb") as f:
    f.write(result.audio_data)

import os
print("Listo: respuesta.mp3")
os.startfile("respuesta.mp3")  