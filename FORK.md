# About this fork

This is a fork of [Dix01/JARVIS](https://github.com/Dix01/JARVIS) (MIT). The original project and almost all of its code belong to its authors. This file lists only the changes made in this fork.

## Security: block cross-origin requests to the local API

JARVIS runs an HTTP + WebSocket server on `127.0.0.1:7341` that can run tools on the machine. Upstream allowed CORS from `*`, so any website open in the same browser could make "simple" requests (a form POST, for example) or open the WebSocket and send commands.

- CORS restricted to loopback origins (`127.0.0.1`, `localhost`, `[::1]`) on any port, so a custom `--port` keeps working.
- An HTTP middleware rejects any request whose `Origin` header is foreign. CORS alone doesn't stop simple requests.
- The WebSocket handshake rejects foreign origins with close code `1008`.
- Requests and handshakes whose `Host` is not a loopback name are rejected, which blocks DNS rebinding (a public domain re-resolving to 127.0.0.1 would otherwise be same-origin and able to read GET responses).

Files: `jarvis/server/origins.py`, `jarvis/server/app.py`, `jarvis/server/ws.py` · Tests: `tests/test_origins.py`

## Fix: Gemini 3 compatibility through the OpenAI-compatible endpoint

- `frequency_penalty` / `presence_penalty` are left out for Google's endpoint, which rejects the whole request (HTTP 400) when they are present.
- Tool calls keep the provider's `extra_content` (Gemini 3's `thought_signature`) and send it back in the history. Without it, the next request fails with HTTP 400.

Files: `jarvis/core/brain.py`, `jarvis/core/orchestrator.py`

## Voice

- Speech recognition on CPU uses Whisper `base` by default (about 1.3 s per sentence on a 4-core i5, against about 4.5 s for `small`), with every core and a `JARVIS_WHISPER_MODEL` override.
- Optional ElevenLabs text-to-speech (`ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`) that falls back to the existing engines on failure.
- Barge-in: speaking over the assistant or pressing `Esc` stops the voice and cancels the running task.

Files: `jarvis/server/routes.py`, `web/src/lib/voice.ts`, `web/src/App.tsx`

## Desktop and localization

- `F2` toggles the window (`Ctrl+Shift+Space` still works), and `--hidden` starts the app in the system tray for launch at Windows startup.
- Spanish (Spain) localization of the UI, boot sequence, persona and speech recognition, with Gemini as the default provider in `config.yaml`.
- `requirements-lite.txt` for a smaller install without the GPU image and 3D stack.

Files: `electron/main.cjs`, `web/src/**`, `config.yaml`, `requirements-lite.txt`
