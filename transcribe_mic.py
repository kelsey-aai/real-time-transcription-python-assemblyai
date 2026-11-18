"""Live microphone transcription with AssemblyAI STT 3.7 Realtime.

Run: python transcribe_mic.py   (Ctrl+C to stop)
"""
import os

import pyaudio
from assemblyai.streaming.v3 import (
    BeginEvent,
    RealTimeError,
    RealTimeEvents,
    RealTimeParameters,
    RealTimeTranscriber,
    RealTimeTranscriberOptions,
    TerminationEvent,
    TurnEvent,
)

SAMPLE_RATE = 16000
FRAMES_PER_BUFFER = 800  # 50 ms of audio at 16 kHz


def on_begin(client: RealTimeTranscriber, event: BeginEvent):
    print(f"Session started: {event.id}")


def on_turn(client: RealTimeTranscriber, event: TurnEvent):
    if not event.transcript:
        return  # ignore empty finals (background noise can trigger them)
    if event.end_of_turn:
        print(f"\r{event.transcript}")  # final: formatted, most accurate
    else:
        print(f"\r{event.transcript}", end="", flush=True)  # partial: replace, don't append


def on_terminated(client: RealTimeTranscriber, event: TerminationEvent):
    print(
        f"\nSession ended: {event.audio_duration_seconds}s of audio, "
        f"{event.session_duration_seconds}s billed session time"
    )


def on_error(client: RealTimeTranscriber, error: RealTimeError):
    print(f"\nError: {error}")


def main():
    client = RealTimeTranscriber(
        RealTimeTranscriberOptions(),
        api_key=os.environ["ASSEMBLYAI_API_KEY"],
    )
    client.on(RealTimeEvents.Begin, on_begin)
    client.on(RealTimeEvents.Turn, on_turn)
    client.on(RealTimeEvents.Termination, on_terminated)
    client.on(RealTimeEvents.Error, on_error)

    client.connect(
        RealTimeParameters(
            speech_model="assemblyai-stt-3-7-realtime",
            sample_rate=SAMPLE_RATE,
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
        client.disconnect(terminate=True)  # closes the session and stops billing


if __name__ == "__main__":
    main()
