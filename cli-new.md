# How to Add New CLI Examples and Topics

This guide describes the repeatable process for adding future examples and topics to SlideSpeak.

It covers two common paths:
- Path A: Add a built-in demo example (no LLM dependency)
- Path B: Add a new real topic workflow (LLM-driven or file-driven)

---

## 1. Decide the Goal Type

Before coding, classify what you want to add:

1. Demo example (deterministic, offline-friendly)
2. New topic template (reusable content structure)
3. New command capability (new subcommand)
4. Variation of existing command (new options/flags)

Use this decision to avoid overengineering.

---

## 2. Follow the Existing Data Contract

All examples and topics should map to the same outline schema expected by the PPT builder.

Required structure:

- title
- introduction
- slides (list)

Each slide should include:

- title
- content (list of blocks)
- speech

Each content block should include:

- bulletPoint
- shortSubPoints (list)
- details (list)

If this schema is broken, PPT generation will fail or produce incomplete slides.

---

## 3. Path A: Add a New Built-In Demo Example

Built-in demos are the fastest way to create reproducible examples.

### Step A1: Add sample payload

In [main.py](main.py), extend the DEMO_SAMPLES dictionary with a new key, for example:

- chemistry-acids-bases
- neural-network-basics
- climate-change-impacts

For each sample, provide:

1. outline object (matching schema)
2. speech transcript string with [PAUSE=1] and [SLIDE CHANGE] markers

### Step A2: Keep speaking flow aligned

Make sure transcript sections separated by [SLIDE CHANGE] match slide order.

Typical mapping:

- Title slide usually has no embedded audio section
- Transcript sections map to content slides in order

### Step A3: Reuse existing demo handler

The current demo handler already accepts a sample key and writes:

- outline JSON
- speech markdown
- PPTX

You only need to add the sample to DEMO_SAMPLES unless command behavior changes.

---

## 4. Path B: Add a New Topic Workflow

If topic content is generated dynamically:

### Step B1: Define user invocation

Decide command shape first, for example:

- generate "topic text"
- generate --topic-file input.txt
- topic --preset cybersecurity

### Step B2: Add parser arguments

In [main.py](main.py), update build_parser() and add flags with clear defaults.

Rules:

1. Keep names explicit (for example --outline, --speech, --pptx)
2. Preserve backward compatibility for existing commands
3. Keep defaults under output/

### Step B3: Implement or extend handler

Use existing helper flow:

- load inputs
- call generation layer
- save outputs
- build PPT
- return non-zero on failure

### Step B4: Handle external dependencies gracefully

If topic generation depends on Ollama or other services, include actionable failure messages.

---

## 5. Optional: Add/Extend Audio Workflow

If the new example/topic needs audio:

1. Ensure speech text includes [SLIDE CHANGE]
2. Run transcript-to-audio command
3. Embed audio into PPT when needed

Current related modules:

- [text2audio_pyttsx3.py](text2audio_pyttsx3.py)
- [text2audio_kokoro.py](text2audio_kokoro.py)
- [text2audio_gtts.py](text2audio_gtts.py)

Current integration command lives in [main.py](main.py) via embed handler.

---

## 6. Validation Checklist for Every New Example/Topic

Run this minimum validation sequence:

1. Compile check
- python -m py_compile main.py

2. CLI surface check
- python main.py --help
- python main.py demo --help (or relevant subcommand)

3. Functional generation
- Run demo/generate/build command for the new topic

4. Artifact validation
- Confirm outline JSON exists
- Confirm speech markdown exists
- Confirm PPTX exists and opens

5. Audio validation (if used)
- Confirm per-slide audio files are created
- Confirm PPTX embedding succeeds

---

## 7. Naming and Content Conventions

Use consistent naming to keep outputs manageable.

Recommended sample key format:

- lowercase-with-hyphens

Recommended output names:

- output/demo-<key>.pptx
- output/enriched_outline.json
- output/presentation_speech.md

Slide quality conventions:

1. 4-7 slides for simple demos
2. Each slide has one main concept
3. Keep bullet wording short
4. Keep details explanatory but concise
5. End with recap or Q&A slide

---

## 8. Common Pitfalls and How to Avoid Them

1. Schema mismatch
- Fix by comparing with existing working sample shape in [main.py](main.py)

2. Transcript-slide misalignment
- Ensure [SLIDE CHANGE] count matches intended content slide sections

3. Re-embedding media into already-embedded deck may fail
- Regenerate clean PPT then embed again if needed

4. Linux TTS missing system backend (pyttsx3)
- Use gTTS or install required system TTS packages

5. Hidden ignored files when committing docs/artifacts
- Check .gitignore and use force add only when intentional

---

## 9. Recommended End-to-End Flow for New Example

Use this sequence for every new sample:

1. Add sample in DEMO_SAMPLES in [main.py](main.py)
2. Run demo command to generate outputs
3. Open PPT and review slide structure
4. Generate audio (optional)
5. Embed audio into PPT (optional)
6. Update README command examples if CLI behavior changed
7. Commit code and docs

---

## 10. Future-Proofing Tips

1. Keep handlers small and single-purpose
2. Put reusable transformations into dedicated modules
3. Add one smoke test per subcommand
4. Keep offline demo path always working
5. Prefer explicit flags over hidden defaults when behavior is critical

Following these steps will make adding new examples and topics faster, safer, and consistent with the current SlideSpeak CLI architecture.
