# SlideSpeak CLI Supplement

This note summarizes how the main CLI workflows differ, what each command produces, and when to use each one.

## Overview

SlideSpeak has five main CLI workflows:

1. `generate`
2. `build`
3. `tts`
4. `embed`
5. `demo`

They are related, but they do different jobs. The main distinction is whether the command:

- calls the LLM,
- rebuilds a PPT from saved files,
- creates audio files,
- embeds audio into the PPT,
- or skips the LLM entirely.

## Workflow Summary

| Command | Uses LLM | Builds PPTX | Writes JSON | Writes speech markdown | Writes audio files | Embeds audio in PPTX | Best for |
|---|---|---|---|---|---|---|---|
| `python main.py generate "<topic>"` | Yes | Yes | Yes | Yes | No | No | Full topic-to-deck generation |
| `python main.py build ...` | No | Yes | No | No | No | No | Rebuilding a deck from saved artifacts |
| `python main.py tts ...` | No | No | No | No | Yes | No | Generating standalone narration audio |
| `python main.py embed ...` | No | Updates existing PPTX | No | No | Yes | Yes | Packaging narration into a PPTX |
| `python main.py demo ...` | No | Yes | Yes | Yes | No | No | Offline sample run without LLM |

## 1. `generate`

Example:

```bash
python main.py generate "Newton's law of universal gravitation" --device CPU
```

What it does:

1. Calls the configured LLM backend.
2. Generates an outline.
3. Enriches slide content.
4. Generates presentation speech.
5. Saves the structured outline to JSON.
6. Saves the narration script to markdown.
7. Builds the PowerPoint deck.

Default outputs:

- `output/enriched_outline.json`
- `output/presentation_speech.md`
- `PPT.pptx`

Use `generate` when you want the full end-to-end content creation workflow from a real topic.

Important detail:

`generate` already includes the PPT-building step. You do not need to run `build` immediately after `generate` unless you later change the saved files and want to rebuild the deck.

## 2. `build`

Example:

```bash
python main.py build --outline output/enriched_outline.json --speech output/presentation_speech.md --pptx PPT.pptx
```

What it does:

1. Reads an existing outline JSON file.
2. Optionally reads an existing speech markdown file.
3. Rebuilds the PowerPoint deck.

What it does not do:

- It does not call the LLM.
- It does not regenerate the JSON.
- It does not regenerate the speech markdown.

Use `build` when:

1. You manually edited `output/enriched_outline.json`.
2. You manually edited `output/presentation_speech.md`.
3. You want to rebuild the deck without paying the cost of another LLM run.
4. You are debugging layout or slide construction only.

This is why `build` is useful even though `generate` already creates a PPTX.

## 3. `tts`

Example:

```bash
python main.py tts --engine pyttsx3 --transcript output/presentation_speech.md --output-dir output/audio
```

What it does:

1. Reads `output/presentation_speech.md`.
2. Splits the transcript into per-slide sections.
3. Writes audio files into the output directory.

What it does not do:

- It does not change `PPT.pptx`.
- It does not embed audio into slides.

Use `tts` when you want narration files as separate assets, such as for testing voices or reusing audio outside PowerPoint.

## 4. `embed`

Example:

```bash
python main.py embed --transcript output/presentation_speech.md --pptx PPT.pptx --audio-dir output/audio
```

What it does:

1. Reads the existing speech markdown.
2. Generates MP3 files using `gTTS`.
3. Opens an existing PPTX.
4. Embeds one audio file into each content slide.
5. Saves the updated PPTX.

What it assumes:

1. A PPTX already exists.
2. The transcript sections align with slide order.

Use `embed` when your goal is not just to create audio files, but to package narration directly inside the PowerPoint.

Important distinction:

`tts` and `embed` are not interchangeable.

- `tts` creates standalone audio files.
- `embed` creates audio and injects it into the PPTX.

## 5. `demo`

Example:

```bash
python main.py demo --sample density-mass-volume --pptx output/demo-density.pptx
```

What it does:

1. Uses a built-in sample fixture.
2. Writes the outline JSON.
3. Writes the speech markdown.
4. Builds a PPTX.

What it does not do:

- It does not call Ollama.
- It does not require a real topic.

Use `demo` when you want a deterministic offline workflow for testing the deck generation path.

## Recommended Workflows

### A. Real topic, full deck generation

```bash
python main.py generate "Newton's law of universal gravitation" --device CPU
```

Use this when you want fresh content from the LLM and a new PPTX.

### B. Edit files, then rebuild only

```bash
python main.py build --outline output/enriched_outline.json --speech output/presentation_speech.md --pptx PPT.pptx
```

Use this after manually adjusting the saved artifacts.

### C. Generate standalone narration only

```bash
python main.py tts --engine pyttsx3 --transcript output/presentation_speech.md --output-dir output/audio
```

Use this when you want audio files but do not need them embedded in PowerPoint.

### D. Add narration into the PPTX

```bash
python main.py embed --transcript output/presentation_speech.md --pptx PPT.pptx --audio-dir output/audio
```

Use this after `generate`, `build`, or `demo` if you want audio packaged in the deck.

### E. Offline workflow without LLM

```bash
python main.py demo --sample density-mass-volume
```

Use this to test the pipeline when Ollama or the network path is unavailable.

## Practical Rule of Thumb

If you only remember one distinction, use this:

1. `generate` = create content and build slides
2. `build` = rebuild slides from saved content
3. `tts` = make narration files
4. `embed` = put narration into the PPTX
5. `demo` = run an offline sample without the LLM