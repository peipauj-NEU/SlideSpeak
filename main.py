import argparse
import json
import shutil
from pathlib import Path

import dictToPpt
import pdf2final_list
import text2audio_pyttsx3
import text2audio_gtts
from text2audio_kokoro import (
    KPipeline,
    VOICE_OPTIONS,
    get_language_code,
    process_transcript as process_kokoro_transcript,
)


DEFAULT_OUTPUT_DIR = Path("output")
DEFAULT_PPTX_PATH = Path("PPT.pptx")
DEFAULT_OUTLINE_PATH = DEFAULT_OUTPUT_DIR / "enriched_outline.json"
DEFAULT_SPEECH_PATH = DEFAULT_OUTPUT_DIR / "presentation_speech.md"


def ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def save_generation_outputs(enriched_outline: dict, speech_text: str, outline_path: Path, speech_path: Path) -> None:
    ensure_output_dir(outline_path)
    ensure_output_dir(speech_path)

    with outline_path.open("w", encoding="utf-8") as file:
        json.dump(enriched_outline, file, ensure_ascii=False, indent=4)

    with speech_path.open("w", encoding="utf-8") as file:
        file.write(speech_text)

def build_presentation(enriched_outline: dict, speech_text: str, pptx_path: Path) -> None:
    dictToPpt.dictToPpt(enriched_outline, speech_text)

    generated_path = Path("PPT.pptx")
    if generated_path.resolve() != pptx_path.resolve():
        ensure_output_dir(pptx_path)
        shutil.copy(generated_path, pptx_path)

def load_outline(outline_path: Path) -> dict:
    with outline_path.open("r", encoding="utf-8") as file:
        return json.load(file)

def load_speech(speech_path: Path) -> str:
    with speech_path.open("r", encoding="utf-8") as file:
        return file.read()

def handle_generate(args: argparse.Namespace) -> int:
    result = pdf2final_list.process(args.topic, device_type=args.device)
    enriched_outline = result["enriched_outline"]
    speech_text = result["speech_text"]

    save_generation_outputs(enriched_outline, speech_text, args.outline, args.speech)
    build_presentation(enriched_outline, speech_text, args.pptx)

    print(f"Saved outline to {args.outline}")
    print(f"Saved speech transcript to {args.speech}")
    print(f"Saved PowerPoint to {args.pptx}")
    return 0

def handle_build(args: argparse.Namespace) -> int:
    enriched_outline = load_outline(args.outline)
    speech_text = load_speech(args.speech) if args.speech.exists() else ""

    build_presentation(enriched_outline, speech_text, args.pptx)
    print(f"Saved PowerPoint to {args.pptx}")
    return 0

def handle_tts(args: argparse.Namespace) -> int:
    if not args.transcript.exists():
        raise SystemExit(f"Transcript file not found: {args.transcript}")

    if args.engine == "pyttsx3":
        try:
            text2audio_pyttsx3.process_transcript(
                str(args.transcript),
                str(args.output_dir),
                rate=args.rate,
                voice_id=args.voice_id,
                volume=args.volume,
            )
        except RuntimeError as error:
            raise SystemExit(
                "pyttsx3 requires eSpeak or eSpeak-ng on Linux. "
                f"Original error: {error}"
            ) from error

        print(f"Generated pyttsx3 audio files in {args.output_dir}")
        return 0

    if args.voice not in VOICE_OPTIONS:
        raise SystemExit(f"Unsupported Kokoro voice '{args.voice}'.")

    try:
        pipeline = KPipeline(lang_code=get_language_code(args.voice))
        process_kokoro_transcript(
            str(args.transcript),
            str(args.output_dir),
            pipeline,
            args.voice,
            args.speed,
            args.gain,
        )
    except Exception as error:
        raise SystemExit(f"Kokoro TTS failed: {error}") from error

    print(f"Generated Kokoro audio files in {args.output_dir}")
    return 0


# ---------------------------------------------------------------------------
# Built-in sample fixture – no LLM required
# ---------------------------------------------------------------------------

DEMO_SAMPLES = {
    "density-mass-volume": {
        "outline": {
            "title": "Density, Mass, and Volume",
            "introduction": (
                "Hello everyone. Today, I will be presenting about Density, Mass, and Volume. "
                "We will explore what each concept means, how they relate to one another, "
                "and how to apply the density formula in practice. [PAUSE=1]"
            ),
            "slides": [
                {
                    "title": "What is Mass?",
                    "content": [
                        {
                            "bulletPoint": "Mass is the amount of matter in an object.",
                            "shortSubPoints": [
                                "Measured in grams (g) or kilograms (kg)",
                                "Remains constant regardless of location",
                                "Not the same as weight",
                            ],
                            "details": [
                                "A 1 kg dumbbell has the same mass on Earth and on the Moon, "
                                "though its weight (force due to gravity) differs.",
                            ],
                        },
                        {
                            "bulletPoint": "Mass is measured with a balance scale.",
                            "shortSubPoints": [
                                "Triple-beam balances used in labs",
                                "Electronic scales measure force and convert to mass",
                            ],
                            "details": [
                                "A balance compares an unknown mass to known reference masses, "
                                "making it gravity-independent.",
                            ],
                        },
                    ],
                    "speech": (
                        "Let's discuss mass. Mass is the measure of how much matter an object "
                        "contains, expressed in grams or kilograms. Unlike weight, mass does not "
                        "change based on gravitational pull, making it a fundamental property of "
                        "matter. [PAUSE=1]"
                    ),
                },
                {
                    "title": "What is Volume?",
                    "content": [
                        {
                            "bulletPoint": "Volume is the amount of space an object occupies.",
                            "shortSubPoints": [
                                "Measured in cubic centimetres (cm\u00b3) or litres (L)",
                                "Solids: length \u00d7 width \u00d7 height",
                                "Irregular solids: water displacement method",
                            ],
                            "details": [
                                "For irregular shapes, submerge the object in water and "
                                "measure the volume of water displaced.",
                            ],
                        },
                        {
                            "bulletPoint": "Liquids are measured with a graduated cylinder.",
                            "shortSubPoints": [
                                "Read the bottom of the meniscus",
                                "Parallax errors occur when not reading at eye level",
                            ],
                            "details": [
                                "The meniscus is the curved surface of a liquid in a narrow "
                                "container caused by surface tension.",
                            ],
                        },
                    ],
                    "speech": (
                        "Now let's discuss volume. Volume describes the three-dimensional space "
                        "an object fills. For regular solids we multiply length, width, and height; "
                        "for irregular objects we rely on the water displacement method. [PAUSE=1]"
                    ),
                },
                {
                    "title": "What is Density?",
                    "content": [
                        {
                            "bulletPoint": "Density is mass per unit volume: D = M \u00f7 V",
                            "shortSubPoints": [
                                "Units: g/cm\u00b3 or kg/m\u00b3",
                                "Intrinsic property \u2014 does not depend on sample size",
                                "Used to identify substances",
                            ],
                            "details": [
                                "Gold has a density of ~19.3 g/cm\u00b3; water is 1.0 g/cm\u00b3. "
                                "Objects denser than water sink; less dense objects float.",
                            ],
                        },
                    ],
                    "speech": (
                        "Density ties mass and volume together through the formula D equals M "
                        "divided by V. It tells us how tightly matter is packed and is an "
                        "intrinsic property, meaning it stays the same no matter how large or "
                        "small the sample is. [PAUSE=1]"
                    ),
                },
                {
                    "title": "The Density Triangle",
                    "content": [
                        {
                            "bulletPoint": "A memory aid for rearranging D = M \u00f7 V",
                            "shortSubPoints": [
                                "Mass   = Density \u00d7 Volume",
                                "Volume = Mass \u00f7 Density",
                                "Density = Mass \u00f7 Volume",
                            ],
                            "details": [
                                "Cover the quantity you want to find; the triangle shows "
                                "whether to multiply or divide the remaining two.",
                            ],
                        },
                    ],
                    "speech": (
                        "The density triangle is a handy tool. Place Mass at the top, Density "
                        "and Volume at the bottom. Cover the unknown variable and the triangle "
                        "shows whether to multiply or divide. [PAUSE=1]"
                    ),
                },
                {
                    "title": "Worked Examples",
                    "content": [
                        {
                            "bulletPoint": "Example 1 \u2014 Find density",
                            "shortSubPoints": [
                                "Mass = 200 g, Volume = 25 cm\u00b3",
                                "D = 200 \u00f7 25 = 8 g/cm\u00b3  (copper)",
                            ],
                            "details": [
                                "Copper has a standard density of 8.96 g/cm\u00b3; "
                                "this is close, showing the formula works.",
                            ],
                        },
                        {
                            "bulletPoint": "Example 2 \u2014 Find volume",
                            "shortSubPoints": [
                                "Mass = 50 g, Density = 2.5 g/cm\u00b3",
                                "V = 50 \u00f7 2.5 = 20 cm\u00b3",
                            ],
                            "details": [
                                "This is consistent with a small piece of glass "
                                "(density \u2248 2.5 g/cm\u00b3).",
                            ],
                        },
                        {
                            "bulletPoint": "Example 3 \u2014 Find mass",
                            "shortSubPoints": [
                                "Density = 1.0 g/cm\u00b3, Volume = 500 cm\u00b3",
                                "M = 1.0 \u00d7 500 = 500 g  (water)",
                            ],
                            "details": [
                                "Pure water at 4 \u00b0C has a density of exactly 1.0 g/cm\u00b3, "
                                "making it the reference standard.",
                            ],
                        },
                    ],
                    "speech": (
                        "Let's solidify the concepts with three worked examples: finding density "
                        "given mass and volume, finding volume given mass and density, and finding "
                        "mass given density and volume. Each follows directly from D equals M "
                        "divided by V. [PAUSE=1]"
                    ),
                },
            ],
        },
        "speech": (
            "Hello everyone. Today, I will be presenting about Density, Mass, and Volume. "
            "We will cover what mass and volume are, how density relates them, the density "
            "triangle memory aid, and three worked examples. [PAUSE=1]\n\n"

            "Let's discuss mass. Mass is the measure of how much matter an object contains, "
            "expressed in grams or kilograms. Unlike weight, mass does not change based on "
            "gravitational pull, making it a fundamental property of matter. [PAUSE=1] "
            "Moving on to our next topic: What is Volume? [SLIDE CHANGE]\n\n"

            "Now let's discuss volume. Volume describes the three-dimensional space an object "
            "fills. For regular solids we multiply length, width, and height; for irregular "
            "objects we rely on the water displacement method. [PAUSE=1] "
            "Moving on to our next topic: What is Density? [SLIDE CHANGE]\n\n"

            "Density ties mass and volume together through the formula D equals M divided by V. "
            "It tells us how tightly matter is packed and is an intrinsic property, meaning it "
            "stays the same no matter how large or small the sample is. [PAUSE=1] "
            "Moving on to our next topic: The Density Triangle. [SLIDE CHANGE]\n\n"

            "The density triangle is a handy tool. Place Mass at the top, Density and Volume "
            "at the bottom. Cover the unknown variable and the triangle shows whether to multiply "
            "or divide. [PAUSE=1] "
            "Moving on to our next topic: Worked Examples. [SLIDE CHANGE]\n\n"

            "Let's solidify the concepts with three worked examples: finding density given mass "
            "and volume, finding volume given mass and density, and finding mass given density "
            "and volume. Each follows directly from the formula D equals M divided by V. [PAUSE=1]\n\n"

            "Thank you for your attention. [PAUSE=1] If you have any questions, "
            "I'd be happy to address them now."
        ),
    },
}


def handle_demo(args: argparse.Namespace) -> int:
    sample = DEMO_SAMPLES.get(args.sample)
    if sample is None:
        available = ", ".join(DEMO_SAMPLES.keys())
        raise SystemExit(f"Unknown sample '{args.sample}'. Available: {available}")

    enriched_outline = sample["outline"]
    speech_text = sample["speech"]

    save_generation_outputs(enriched_outline, speech_text, args.outline, args.speech)
    build_presentation(enriched_outline, speech_text, args.pptx)

    print(f"Sample  : {args.sample}")
    print(f"Outline : {args.outline}")
    print(f"Speech  : {args.speech}")
    print(f"PPTX    : {args.pptx}")
    return 0


def handle_embed(args: argparse.Namespace) -> int:
    """Generate gTTS audio and embed each slide's MP3 into the PPTX."""
    from pptx import Presentation
    from pptx.util import Inches, Emu

    transcript_path = args.transcript
    pptx_path = args.pptx

    if not transcript_path.exists():
        raise SystemExit(f"Transcript not found: {transcript_path}")
    if not pptx_path.exists():
        raise SystemExit(f"PPTX not found: {pptx_path}")

    print(f"Generating audio from: {transcript_path}")
    mp3_files = text2audio_gtts.process_transcript(
        str(transcript_path), str(args.audio_dir), lang=args.lang
    )

    prs = Presentation(str(pptx_path))
    slides = list(prs.slides)
    print(f"PPTX has {len(slides)} slides; generated {len(mp3_files)} audio segments.")

    # Embed each MP3 into its corresponding slide (skip title slide if counts differ)
    offset = len(slides) - len(mp3_files)  # e.g. 1 when title slide has no audio
    for idx, mp3_path in enumerate(mp3_files):
        slide_idx = idx + offset
        if slide_idx >= len(slides):
            print(f"  Warning: no slide for audio segment {idx + 1}, skipping.")
            break
        slide = slides[slide_idx]
        # Place the audio shape off-screen (hidden in presenter view)
        slide.shapes.add_movie(
            mp3_path,
            left=Emu(0), top=Emu(0),
            width=Inches(0.5), height=Inches(0.5),
            mime_type="audio/mpeg",
        )
        print(f"  Embedded {mp3_path} into slide {slide_idx + 1}")

    prs.save(str(pptx_path))
    print(f"Saved updated PPTX: {pptx_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Headless SlideSpeak CLI for generating presentations and TTS assets."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate outline, speech transcript, and PPTX from a topic using the configured LLM.",
    )
    generate_parser.add_argument("topic", help="Presentation topic to generate.")
    generate_parser.add_argument(
        "--device",
        choices=["CPU", "NPU"],
        default="CPU",
        help="Execution backend for content generation.",
    )
    generate_parser.add_argument("--outline", type=Path, default=DEFAULT_OUTLINE_PATH, help="Path to save enriched outline JSON.")
    generate_parser.add_argument("--speech", type=Path, default=DEFAULT_SPEECH_PATH, help="Path to save presentation speech markdown.")
    generate_parser.add_argument("--pptx", type=Path, default=DEFAULT_PPTX_PATH, help="Path to save the generated PowerPoint file.")
    generate_parser.set_defaults(handler=handle_generate)

    demo_parser = subparsers.add_parser(
        "demo",
        help="Build a sample PPTX from a built-in fixture without any LLM or network call.",
    )
    demo_parser.add_argument(
        "--sample",
        default="density-mass-volume",
        choices=list(DEMO_SAMPLES.keys()),
        help="Which built-in sample to use (default: density-mass-volume).",
    )
    demo_parser.add_argument(
        "--outline",
        type=Path,
        default=DEFAULT_OUTLINE_PATH,
        help="Path to save enriched outline JSON.",
    )
    demo_parser.add_argument(
        "--speech",
        type=Path,
        default=DEFAULT_SPEECH_PATH,
        help="Path to save presentation speech markdown.",
    )
    demo_parser.add_argument(
        "--pptx",
        type=Path,
        default=DEFAULT_PPTX_PATH,
        help="Path to save the generated PowerPoint file.",
    )
    demo_parser.set_defaults(handler=handle_demo)

    build_parser_cmd = subparsers.add_parser(
        "build",
        help="Build a PPTX from an existing outline JSON and optional speech transcript.",
    )
    build_parser_cmd.add_argument("--outline", type=Path, default=DEFAULT_OUTLINE_PATH, help="Path to enriched outline JSON.")
    build_parser_cmd.add_argument("--speech", type=Path, default=DEFAULT_SPEECH_PATH, help="Path to presentation speech markdown.")
    build_parser_cmd.add_argument("--pptx", type=Path, default=DEFAULT_PPTX_PATH, help="Path to save the generated PowerPoint file.")
    build_parser_cmd.set_defaults(handler=handle_build)

    tts_parser = subparsers.add_parser(
        "tts",
        help="Generate per-slide audio files from an existing transcript.",
    )
    tts_parser.add_argument("--engine", choices=["pyttsx3", "kokoro"], default="pyttsx3", help="TTS backend to use.")
    tts_parser.add_argument("--transcript", type=Path, default=DEFAULT_SPEECH_PATH, help="Path to the presentation speech markdown file.")
    tts_parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR / "audio", help="Directory where per-slide WAV files will be written.")
    tts_parser.add_argument("--rate", type=int, default=150, help="Speech rate for pyttsx3.")
    tts_parser.add_argument("--voice-id", type=int, default=None, help="Voice index for pyttsx3.")
    tts_parser.add_argument("--volume", type=float, default=1.0, help="Output volume for pyttsx3.")
    tts_parser.add_argument("--voice", default=VOICE_OPTIONS[0], help="Voice name for Kokoro.")
    tts_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed for Kokoro.")
    tts_parser.add_argument("--gain", type=float, default=1.0, help="Output gain for Kokoro.")
    tts_parser.set_defaults(handler=handle_tts)

    embed_parser = subparsers.add_parser(
        "embed",
        help="Generate per-slide audio via gTTS and embed it into an existing PPTX.",
    )
    embed_parser.add_argument("--transcript", type=Path, default=DEFAULT_SPEECH_PATH, help="Path to the presentation speech markdown.")
    embed_parser.add_argument("--pptx", type=Path, default=DEFAULT_PPTX_PATH, help="PPTX file to embed audio into.")
    embed_parser.add_argument("--audio-dir", type=Path, default=DEFAULT_OUTPUT_DIR / "audio", help="Directory for intermediate MP3 files.")
    embed_parser.add_argument("--lang", default="en", help="gTTS language code (default: en).")
    embed_parser.set_defaults(handler=handle_embed)

    return parser

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)

if __name__ == "__main__":
    raise SystemExit(main())
