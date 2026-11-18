"""Stream a raw 16 kHz, 16-bit mono PCM file to AssemblyAI STT 3.7 Realtime at real-time pace.

Convert first, for example: ffmpeg -i call.wav -ar 16000 -ac 1 -f s16le call.pcm
Run: python transcribe_file.py call.pcm
"""
import os
import sys
import time

from assemblyai.streaming.v3 import (
    RealTimeEvents,
    RealTimeParameters,
    RealTimeTranscriber,
    RealTimeTranscriberOptions,
    TurnEvent,
)

SAMPLE_RATE = 16000
CHUNK_BYTES = 3200  # 100 ms of 16-bit mono audio at 16 kHz


def file_chunks(path, chunk_size=CHUNK_BYTES):
    """Yield PCM chunks, paced to real time so the session behaves like a live source."""
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk
            time.sleep(chunk_size / (SAMPLE_RATE * 2))


def on_turn(client: RealTimeTranscriber, event: TurnEvent):
    if event.end_of_turn and event.transcript:
        print(event.transcript)


def main(path):
    client = RealTimeTranscriber(
        RealTimeTranscriberOptions(terminate_timeout=30.0),
        api_key=os.environ["ASSEMBLYAI_API_KEY"],
    )
    client.on(RealTimeEvents.Turn, on_turn)
    client.connect(
        RealTimeParameters(speech_model="assemblyai-stt-3-7-realtime", sample_rate=SAMPLE_RATE)
    )
    try:
        client.stream(file_chunks(path))
    finally:
        client.disconnect(terminate=True)


if __name__ == "__main__":
    main(sys.argv[1])
