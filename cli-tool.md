# SlideSpeak Development Summary: Dependency Setup and Headless CLI Build

## 1) Project Goal and Starting Point

SlideSpeak started as a GUI-first Python project for:
- generating presentation outlines and slide content from prompts,
- building a PowerPoint deck,
- generating speech text and optional slide audio.

The original flow relied heavily on GUI interactions and local runtime dependencies (Ollama, OS-specific behaviors, and TTS engines).

## 2) Dependency Audit and Environment Preparation

A full environment and import audit was performed to identify what was needed for reliable execution in a Linux dev container.

### 2.1 Runtime setup
- Confirmed Python and pip availability.
- Created and activated a virtual environment.
- Installed required Python packages for generation, PPT building, and TTS.

### 2.2 Core dependencies installed
- requests
- python-pptx
- pyttsx3
- soundfile
- numpy
- kokoro
- torch and related transitive dependencies required by kokoro stack

### 2.3 Requirements file added
A requirements file was added so environment setup is reproducible:
- requirements.txt
- Includes platform-aware pywin32 entry (Windows only).

### 2.4 Important dependency caveats discovered
- Linux container is headless (no DISPLAY): GUI cannot be the only entry point.
- Ollama not running by default in container, so LLM generation can fail unless service/model is available.
- Kokoro model files must be present in project root for kokoro TTS.
- pyttsx3 on Linux requires espeak/espeak-ng availability.

## 3) Cross-Platform Stability Fixes

To make the project runnable outside Windows and outside desktop environments, compatibility fixes were made.

### 3.1 Optional win32com in PPT post-processing
File updated: dictToPpt.py
- Wrapped win32com import in safe fallback handling.
- Added runtime guard so Windows-only shrinking behavior fails with a clear message rather than crashing import on Linux.

### 3.2 GUI file opening made cross-platform
File updated: gui.py
- Replaced Windows-only startfile call with platform-aware open behavior.
- Added checks and actionable error handling when no opener is available.

These changes removed hard Windows assumptions and improved Linux portability.

## 4) Headless CLI Design and Implementation

The major architectural improvement was implementing a true headless CLI path in main.py.

### 4.1 CLI subcommand model
The CLI was implemented with argparse and split into subcommands:
- generate: prompt to outline + speech + pptx (LLM path)
- build: create pptx from existing outline/speech files (no LLM required)
- tts: generate per-slide audio from transcript using pyttsx3 or kokoro
- demo: create a full presentation from a built-in fixture (no LLM required)
- embed: generate gTTS audio and embed into an existing pptx

### 4.2 Why this structure
- Separates concerns (generation, build, TTS, embedding).
- Enables deterministic operation in CI/containers.
- Provides fallback paths when LLM or GUI is unavailable.

### 4.3 Supporting helper flow
main.py now includes helper functions to:
- load and save outline/speech artifacts,
- call generation pipeline,
- build pptx from existing artifacts,
- run TTS backends with backend-specific validation,
- run demo fixture generation,
- embed audio into slides.

## 5) Demo Fixture (No-LLM Path)

A built-in demo sample was added for:
- density-mass-volume

This fixture includes:
- complete outline schema compatible with PPT builder,
- per-slide bullets/subpoints/details,
- full speech transcript with pause and slide-change markers.

Outcome:
- Allows full end-to-end testing without Ollama.
- Produces reproducible outputs for local/headless validation.

## 6) Audio Integration Workflow

The project now supports transcript-to-audio and deck integration.

### 6.1 New gTTS module
File added: text2audio_gtts.py
- Splits transcript by slide markers.
- Cleans pause/transition tags.
- Generates one MP3 per slide section.

### 6.2 Embed command in CLI
Implemented in main.py via embed subcommand:
- Reads transcript,
- generates MP3s into output/audio,
- embeds each MP3 into corresponding content slide in pptx.

### 6.3 Mapping behavior
- Deck has a title slide, while transcript sections target content slides.
- Embedding uses offset logic so slide audio is attached to slides 2-N.

## 7) Validation and Test Runs Performed

The following validations were executed during development:
- Python compile check for main.py.
- Help/argparse checks for CLI command surface.
- Headless build execution creating pptx from existing artifacts.
- Demo generation execution creating demo-density.pptx.
- TTS generation checks and runtime dependency error handling.
- Audio embedding execution with generated MP3 files and updated pptx.

Validated outputs observed:
- output/enriched_outline.json
- output/presentation_speech.md
- output/demo-density.pptx
- output/audio/slide1.mp3 ... slide5.mp3

## 8) Edge Cases and Known Behavior

- Re-running embed on an already media-embedded deck can trigger a python-pptx media-part bug in some cases.
- Reliable workaround used: regenerate clean demo deck, then run embed.
- pyttsx3 remains dependent on espeak/espeak-ng in Linux environments.
- generate still depends on reachable LLM backend (Ollama/NPU endpoint).

## 9) Documentation and Delivery Status

Project documentation was updated to describe headless CLI usage, and code was committed and pushed to the remote repository.

Net result:
- SlideSpeak now supports practical headless operation,
- deterministic no-LLM demo generation,
- and transcript-driven audio embedding into presentation slides.

## 10) Recommended Next Hardening Steps

1. Make embed idempotent by detecting/removing prior media relations before re-embedding.
2. Add .gitignore entries for local artifacts like .venv and output/audio.
3. Add a non-network offline TTS backend for container reliability.
4. Add automated smoke tests for demo, build, tts, and embed subcommands.
5. Add a single command pipeline that runs demo -> tts -> embed with one invocation.
