import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import azure.cognitiveservices.speech as speechsdk

def index(request):
    voices = [
        "es-ES-ElviraNeural",
        "es-ES-AlvaroNeural",
        "es-MX-DaliaNeural",
        "es-MX-JorgeNeural",
        "es-AR-ElenaNeural",
        "es-AR-TomasNeural",
        "es-BO-SofiaNeural",
        "es-BO-MarceloNeural",
        "es-CL-CatalinaNeural",
        "es-CL-LorenzoNeural",
        "es-CO-SalomeNeural",
        "es-US-PalomaNeural",
        
    ]
    styles = [
        "neutral", "cheerful", "empathetic", "newscast",
        "customerservice", "sad", "excited", "calm", "angry"
    ]
    return render(request, "ttsapp/index.html", {"voices": voices, "styles": styles})

@csrf_exempt
@require_POST
def tts_azure(request):
    try:
        SPEECH_KEY = settings.SPEECH_KEY
        SPEECH_REGION = settings.SPEECH_REGION
        if not (SPEECH_KEY and SPEECH_REGION):
            return HttpResponseBadRequest("Falta SPEECH_KEY o SPEECH_REGION. Revisa .env y settings.py")

        body = json.loads(request.body.decode("utf-8"))
        text  = (body.get("text") or "").strip()
        if not text:
            return HttpResponseBadRequest("texto vacío")

        voice = body.get("voice", "es-ES-ElviraNeural")
        style = body.get("style", "neutral")
        styledegree = str(body.get("styledegree", "1.2"))
        rate  = body.get("rate", "+0%")
        pitch = body.get("pitch", "+0st")
        pause_ms = str(body.get("pause_ms", "200ms"))
        use_sentence_silence = bool(body.get("use_sentence_silence", True))

        sil_tag = f"<mstts:silence type='Sentenceboundary' value='{pause_ms}'/>" if use_sentence_silence else ""

        ssml = f"""
<speak version='1.0' xml:lang='es-ES' xmlns:mstts='https://www.w3.org/2001/mstts'>
  <voice name='{voice}'>
    {sil_tag}
    <mstts:express-as style='{style}' styledegree='{styledegree}'>
      <prosody rate='{rate}' pitch='{pitch}'>
        {text}
      </prosody>
    </mstts:express-as>
  </voice>
</speak>""".strip()

        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3
        )

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        result = synthesizer.speak_ssml_async(ssml).get()

        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            det = result.cancellation_details
            msg = f"Azure TTS error: {det.reason if det else 'desconocido'}"
            if det and det.error_details:
                msg += f" | {det.error_details}"
            return HttpResponseBadRequest(msg)

        audio_bytes = result.audio_data
        print(f"[TTS] Bytes generados: {len(audio_bytes)}")
        if not audio_bytes:
            return HttpResponseBadRequest("Azure TTS devolvió audio vacío")

        resp = HttpResponse(audio_bytes, content_type="audio/mpeg")
        resp["Content-Disposition"] = 'inline; filename="voz.mp3"'
        return resp

    except Exception as e:
        return HttpResponseBadRequest(str(e))

@csrf_exempt
def voices(request):
    try:
        from django.conf import settings
        import azure.cognitiveservices.speech as speechsdk

        if not (settings.SPEECH_KEY and settings.SPEECH_REGION):
            return JsonResponse({"ok": False, "error": "Falta SPEECH_KEY o SPEECH_REGION"}, status=400)

        cfg = speechsdk.SpeechConfig(subscription=settings.SPEECH_KEY, region=settings.SPEECH_REGION)
        synth = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=None)
        v = synth.get_voices_async().get()

        es = []
        for voice in (v.voices or []):
            if getattr(voice, "locale", "").startswith("es"):
                gender = getattr(voice, "gender", None)
                gender_str = None
                if gender is not None:
                    gender_str = getattr(gender, "name", str(gender))

                es.append({
                    "name": voice.name,
                    "shortName": getattr(voice, "short_name", None) or voice.name,
                    "locale": voice.locale,
                    "gender": gender_str,
                })

        return JsonResponse({"ok": True, "voices": es})

    except Exception as e:
        import traceback; traceback.print_exc()
        return JsonResponse({"ok": False, "error": str(e)}, status=400)
