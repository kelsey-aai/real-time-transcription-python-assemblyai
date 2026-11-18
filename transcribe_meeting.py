"""Live meeting transcript with speaker labels on AssemblyAI STT 3.7 Realtime.

Run: python transcribe_meeting.py   (Ctrl+C to stop)
"""
import os

import pyaudio
from assemblyai.streaming.v3 import (
    RealTimeEvents,
    RealTimeParameters,
    RealTimeTranscriber,
    RealTimeTranscriberOptions,
    TurnEvent,
)

SAMPLE_RATE = 16000
FRAMES_PER_BUFFER = 800


def on_turn(client: RealTimeTranscriber, event: TurnEvent):
    if event.end_of_turn and event.transcript:
        speaker = event.speaker_label or "PENDING"
        print(f"[{speaker}] {event.transcript}")


def main():
    client = RealTimeTranscriber(
        RealTimeTranscriberOptions(),
        api_key=os.environ["ASSEMBLYAI_API_KEY"],
    )
    client.on(RealTimeEvents.Turn, on_turn)
    client.connect(
        RealTimeParameters(
            speech_model="assemblyai-stt-3-7-realtime",
            sample_rate=SAMPLE_RATE,
            speaker_labels=True,
            max_speakers=4,  # hard cap; leave a little headroom
            keyterms_prompt=["AssemblyAI", "Q3 roadmap"],
        )
    )

    pa = pyaudio.PyAudio()
    mic = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
    )
    try:
        while True:
            client.stream(mic.read(FRAMES_PER_BUFFER, exception_on_overflow=False))
    except KeyboardInterrupt:
        pass
    finally:
        mic.stop_stream()
        mic.close()
        pa.terminate()
        client.disconnect(terminate=True)


if __name__ == "__main__":
    main()
