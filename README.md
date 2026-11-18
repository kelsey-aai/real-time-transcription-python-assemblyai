# Real-time transcription in Python with AssemblyAI STT 3.7 Realtime

Companion code for the AssemblyAI blog post [Real-time transcription in Python with AssemblyAI's streaming SDK](https://www.assemblyai.com/blog/real-time-transcription-in-python).

Every script uses **AssemblyAI STT 3.7 Realtime** (`speech_model="assemblyai-stt-3-7-realtime"`, $0.30/hr), the streaming model built for notetakers, captions, meetings and other live transcription. If you're building a voice agent, switch `speech_model` to `assemblyai-stt-3-7-realtime-agent` (AssemblyAI STT 3.7 Realtime Agent, $0.45/hr).

| Script | What it does |
|---|---|
| `transcribe_mic.py` | Live microphone transcription: partials rendered in place, finals committed |
| `transcribe_meeting.py` | Live meeting transcript with real-time speaker labels and keyterms |
| `transcribe_file.py` | Streams a raw 16 kHz PCM file at real-time pace (telephony bridges, recordings) |
| `token_server.py` | Minimal server that mints short-lived streaming tokens for client-side apps |

## Setup

Requires Python 3.9+ and the PortAudio library for microphone capture.

```bash
# macOS
brew install portaudio
# Debian/Ubuntu
sudo apt install portaudio19-dev

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ASSEMBLYAI_API_KEY=your_api_key_here   # or copy .env.example
```

Get a free API key at [assemblyai.com/dashboard/signup](https://www.assemblyai.com/dashboard/signup).

## Run

```bash
python transcribe_mic.py
python transcribe_meeting.py
python transcribe_file.py call.pcm   # ffmpeg -i call.wav -ar 16000 -ac 1 -f s16le call.pcm
python token_server.py               # GET http://localhost:8000/token
```

## Billing note

Streaming is billed on how long the WebSocket session stays open, not on the audio you send. Every script calls `client.disconnect(terminate=True)` in a `finally` block. A session you never close auto-closes after 3 hours and is billed for the full duration.

## Notes

- Requires `assemblyai` 1.10.1 or later; earlier SDK versions don't list the STT 3.7 model IDs.
- `format_turns`, `end_of_turn_confidence_threshold` and `speaker_labels_revision_interval_ms` are no longer documented and aren't used here.
- Docs: [Streaming quickstart](https://www.assemblyai.com/docs/streaming/getting-started/transcribe-streaming-audio) · [Turn detection](https://www.assemblyai.com/docs/streaming/turn-detection) · [Speaker labels](https://www.assemblyai.com/docs/streaming/label-speakers-and-separate-channels)
