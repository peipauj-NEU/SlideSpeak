# CLI Tool Tutorial: From Idea to a Usable Command-Line App

This tutorial explains how to design and build a command-line interface (CLI) tool in a clean, maintainable way.

It is general-purpose, but uses SlideSpeak as an illustration for concrete examples.

---

## 1) What Is a CLI Tool?

A CLI tool is a program you run from a terminal, often like this:

```bash
python main.py <subcommand> [options]
```

Good CLI tools are:
- predictable,
- scriptable,
- easy to automate in CI/servers,
- usable without a graphical interface.

---

## 2) Start With User Workflows, Not Code

Before writing code, define user jobs.

For SlideSpeak, key jobs were:
- create content from a topic,
- build a PPT from existing files,
- generate audio from transcript,
- run a complete demo without external LLM,
- embed audio into slides.

Each job became one subcommand:
- `generate`
- `build`
- `tts`
- `demo`
- `embed`

General rule:
- one user goal = one subcommand.

---

## 3) Choose a CLI Structure

For Python, common choices:
- `argparse` (stdlib, no extra dependency)
- `click` / `typer` (more ergonomic, extra dependency)

SlideSpeak uses `argparse`, which is a strong default.

Recommended high-level layout:

```python
# main.py

def build_parser():
    # define global parser and subcommands
    ...

def handle_generate(args):
    ...

def handle_build(args):
    ...

def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)

if __name__ == "__main__":
    raise SystemExit(main())
```

Why this works:
- parsing and business logic are separated,
- each command has a dedicated handler,
- easy to test handlers directly.

---

## 4) Define Inputs and Outputs Explicitly

A robust CLI should make I/O locations explicit and overridable.

Pattern used in SlideSpeak:
- default paths like `output/enriched_outline.json`,
- override with flags such as `--outline`, `--speech`, `--pptx`, `--output-dir`.

Example invocation:

```bash
python main.py build \
  --outline output/enriched_outline.json \
  --speech output/presentation_speech.md \
  --pptx output/demo-density.pptx
```

Design tips:
- provide sensible defaults,
- keep flags descriptive,
- avoid hidden magic paths when possible.

---

## 5) Use Subcommands for Separation of Concerns

Do not overload one command with too many modes.

In SlideSpeak:
- `generate` calls LLM workflow,
- `build` only assembles PPT from saved artifacts,
- `tts` only handles transcript-to-audio,
- `embed` only inserts audio into PPT,
- `demo` produces deterministic sample data.

This separation enables:
- partial reruns,
- easier debugging,
- cleaner error reporting,
- less coupling between components.

---

## 6) Add a Deterministic Demo Mode Early

A common CLI mistake is requiring cloud services for every test run.

SlideSpeak solves this with `demo`:
- hardcoded sample data (`density-mass-volume`),
- no Ollama dependency,
- reproducible output every run.

Why this matters generally:
- speeds development,
- improves reliability in offline/headless environments,
- gives a stable acceptance test.

---

## 7) Handle Platform Differences Proactively

CLI tools often run in containers, Linux servers, macOS laptops, and Windows PCs.

SlideSpeak had to address:
- Windows-only `win32com` usage,
- Windows-only file opener assumptions,
- Linux TTS engine requirements.

General strategy:
1. Guard optional imports with clear fallbacks.
2. Check runtime prerequisites before heavy work.
3. Print actionable error messages.

Bad error:
- stack trace with no user guidance.

Good error:
- "pyttsx3 requires eSpeak or eSpeak-ng on Linux."

---

## 8) Design for Headless Operation

Headless means no GUI and often no display server.

If your tool originally had a GUI, build a non-GUI entry path that covers core functionality.

Checklist:
- no dependency on Tk event loop,
- all operations invokable via terminal flags,
- output files are machine-readable,
- command exit codes reflect success/failure.

---

## 9) Build a Clear Error Model

Use this pattern in each handler:
1. Validate inputs early.
2. Fail fast with readable messages.
3. Keep stack traces for unexpected internal errors.

Example structure:

```python
if not transcript_path.exists():
    raise SystemExit(f"Transcript not found: {transcript_path}")
```

For expected external failures (service unavailable, missing model files), convert exceptions into concise user-facing errors.

---

## 10) Keep Outputs Predictable and Reusable

CLI tools are often chained.

SlideSpeak writes stable artifacts:
- JSON outline,
- markdown speech transcript,
- PPTX,
- per-slide audio files.

This enables workflows like:
1. `demo`
2. `tts` or `embed`
3. inspect/share outputs

General advice:
- output file names should be deterministic unless explicitly random.

---

## 11) Include a Quick Command Cookbook in Docs

Every CLI project should document common commands.

Example cookbook (SlideSpeak-style):

```bash
# Build from an existing outline/speech
python main.py build --outline output/enriched_outline.json --speech output/presentation_speech.md --pptx output/deck.pptx

# Generate audio from transcript
python main.py tts --engine pyttsx3 --transcript output/presentation_speech.md --output-dir output/audio

# Create deterministic sample deck
python main.py demo --pptx output/demo-density.pptx

# Generate + embed mp3 audio into deck
python main.py embed --transcript output/presentation_speech.md --pptx output/demo-density.pptx
```

Also ensure `--help` is useful for the root parser and all subcommands.

---

## 12) Validate Iteratively

For each new command, run a minimum validation sequence:
1. parser/help check
2. compile/import check
3. happy-path run
4. one failure-path run

For SlideSpeak-style workflows:
- `python -m py_compile main.py`
- `python main.py --help`
- `python main.py demo --pptx output/demo-density.pptx`
- `python main.py embed --transcript output/presentation_speech.md --pptx output/demo-density.pptx`

---

## 13) Version Control and Release Discipline

When the CLI is stable enough:
1. stage only relevant files,
2. commit with a precise message,
3. push branch,
4. keep generated local artifacts untracked (`.venv`, large temp outputs).

This keeps repository history clean and reproducible.

---

## 14) A Reusable Blueprint for Any CLI Project

Use this blueprint in new projects:

1. Define 3–5 user jobs.
2. Map each job to one subcommand.
3. Implement handlers with explicit input/output flags.
4. Add deterministic demo command.
5. Add robust platform/environment checks.
6. Document command cookbook.
7. Add smoke tests and CI checks.

If you follow these steps, your CLI will usually be easier to maintain than a GUI-first workflow and much easier to automate.

---

## 15) Optional Next Improvements (for this project or any similar one)

- Make embedding idempotent (safe to rerun on same file).
- Add automated integration tests per subcommand.
- Add a single pipeline command that chains multiple steps.
- Add offline-first TTS fallback backend.
- Add structured logging (`--verbose`, `--quiet`, JSON log option).

These improvements turn a functional CLI into a production-grade tool.
