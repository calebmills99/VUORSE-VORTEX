---
name: comfyui-voice-pipeline
description: Generate character voices using TTS, voice cloning, and lip-sync tools. Supports Chatterbox, F5-TTS, TTS Audio Suite, RVC, and ElevenLabs. Use when creating speech audio for characters or syncing audio to video.
---

# ComfyUI Voice Pipeline

> All recommendations in this skill are subordinate to `state/inventory.json`, `foundation/hardware-profile.md`, and current version constraints.

Creates character voices through TTS/voice cloning and synchronizes them with generated video.

Before choosing a path, verify the required node, model, executable, or API integration.
Classify each candidate as local ComfyUI, external local tooling, or hosted API. A named
tool below is never evidence that it is available.

## Voice Generation Decision Tree

```
VOICE REQUEST
    |
    |-- Have reference audio of target voice?
    |   |-- Yes → Compare installed cloning/conversion engines against their versioned requirements
    |   |-- Hosted service acceptable → ElevenLabs API, if configured
    |
    |-- No reference audio?
    |   |-- Need emotion control → Select an installed engine exposing emotion controls
    |   |-- Need multi-language → Select an installed engine supporting the target language
    |   |-- Need voice design → ElevenLabs Voice Design (describe voice)
    |   |-- Quick prototype → Available default voice
    |
    |-- Need multi-speaker dialog?
    |   |-- Select an installed engine exposing speaker switching
    |
    |-- Need lip-sync?
    |   |-- Wav2Lip installed? → Validate it on the target face and footage
    |   |-- Need head movement/expression transfer → Verify SadTalker or LivePortrait availability
    |   |-- Need long-form output → Verify an installed long-form workflow and its limits
```

## Tool Reference

### Chatterbox (Local Candidate)

Verify the installed version, supported tags, reference-audio requirements, and runtime
before selecting it. Upstream benchmark claims are not local validation.

**Paralinguistic tags:**
```
[laugh] [chuckle] [sigh] [gasp] [cough] [clear throat]
[whisper] [excited] [sad] [angry] [surprised]
```

**Key parameter**: `exaggeration` (0.25-2.0) controls expressiveness.

Confirm the installed version's segment limit before splitting long content.

### F5-TTS

Verify reference length, language support, and license from the installed version's model card.

**Requirements**: Reference audio must be paired with `.wav` + `.txt` (matching transcription).

**Languages**: English, German, Spanish, French, Japanese, Hindi, Thai, Portuguese.

### TTS Audio Suite

Verify which engines, languages, and speaker-switching features the installed node exposes.

**Special features:**
- Character switching: `[CharacterName]` tags
- Language switching: `[de:Alice]`, `[fr:Bob]`
- Pause control: `[pause:1s]`
- SRT timing sync

**Integrates**: F5-TTS, Chatterbox, Higgs Audio 2, VibeVoice, IndexTTS-2, RVC.

### IndexTTS-2

Verify the installed version's emotion controls and per-segment parameters.

**Emotions**: happy, angry, sad, surprised, afraid, disgusted, calm, melancholic.

### RVC (Voice Conversion)

**Use case**: Train a model on target voice (10+ min audio), then convert any TTS output.

**Pipeline**: `Text → Any TTS → Base Audio → RVC Model → Character Voice`

Derive training duration and feature extraction from the selected RVC implementation and dataset.

### ElevenLabs (Hosted API)

Treat ElevenLabs as an external service, never as a locally installed ComfyUI model.
Use it only when the configured integration is available.

**Tiers:**
- Instant Clone: 1-minute sample, good quality
- Professional Clone: 30+ minutes (3h ideal), near-indistinguishable
- Voice Design: Describe voice in text (no sample needed)

## Voice Profile Setup

For each character, establish a voice profile in `projects/{project}/characters/{name}/profile.yaml`:

```yaml
voice:
  cloned: true
  model: "chatterbox"
  sample_file: "references/voice_sample.wav"
  settings:
    exaggeration: 1.2
    default_emotion: "neutral"
  notes: "[voice qualities, accent, pacing, and delivery]"
```

## Script Preparation

### Text Formatting for TTS

1. **Punctuation matters**: Commas create pauses, periods create stops
2. **Phonetic hints**: Spell unusual words phonetically if mispronounced
3. **Emotion cues**: Use Chatterbox tags or split by emotion for IndexTTS-2
4. **Length**: Split into 30-40 second segments for Chatterbox limit

### Multi-Speaker Script

```
[Speaker A] Hello! *laughs* I've been looking forward to this.
[pause:0.5s]
[Speaker B] [excited] Same here! Let's dive right in.
[Speaker A] [whisper] But first, I need to tell you something...
```

## Audio Post-Processing

### Requirements for Lip-Sync Input

- Sample rate: 16-24kHz (model dependent)
- Format: WAV (uncompressed)
- Mono channel
- Trim leading silence
- Add 0.2s trailing silence
- Normalize to -3dB peak

### FFmpeg Processing

```bash
# Convert to mono 24kHz WAV, normalized
ffmpeg -i input.wav -ac 1 -ar 24000 -af "loudnorm=I=-16:TP=-3" output.wav

# Trim silence from start/end
ffmpeg -i input.wav -af "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse" trimmed.wav

# Concatenate segments
ffmpeg -f concat -safe 0 -i filelist.txt -c copy combined.wav
```

## Lip-Sync Methods

### Wav2Lip

**Settings:**
```
wav2lip_model: "wav2lip_gan.pth"  # Better than wav2lip.pth
face_detect_batch: 16
nosmooth: false
pad_bottom: 10
```

**MUST post-process**: CodeFormer (fidelity 0.7) after Wav2Lip output.

### SadTalker (Head Movement)

**Settings:**
```
preprocess: "full"     # Better for novel faces
enhancer: "gfpgan"
pose_style: 10-20      # Natural conversation range
```

### LivePortrait (Expression Control)

**Settings:**
```
lip_zero: 0.03         # Reduces unnatural lip movement
stitching: true        # Seamless face blending
```

**Use when**: The installed workflow supports expression transfer from a driving video.

### LatentSync (Verify Installed Version)

ByteDance model trained at 512x512 with TREPA modules for temporal consistency.

### InfiniteTalk (Long-Form Candidate)

For videos longer than standard lip-sync limits. Integrates with Wan for joint generation.

## Complete Talking Head Workflow

### Pipeline A: Quick (Image → Talk)

```
1. [Text] → Chatterbox/F5-TTS → audio.wav
2. [Character Image] + audio.wav → SadTalker → video.mp4
3. video.mp4 → GFPGAN/CodeFormer → final.mp4
```
Runtime and quality: benchmark the installed pipeline on the target footage.

### Pipeline B: Quality (Image → Video → Lip-Sync)

```
1. [Text] → Chatterbox → audio.wav
2. [Character Image] → Wan I2V → base_video.mp4
   Prompt: "person talking, slight head movement, indoor"
3. base_video.mp4 + audio.wav → Wav2Lip → lipsync.mp4
4. lipsync.mp4 → FaceDetailer batch → enhanced.mp4
5. enhanced.mp4 → Color correct + Deflicker → final.mp4
```
Runtime and quality: benchmark the installed pipeline on the target footage.

### Pipeline C: Premium (Expression Transfer)

```
1. Record driving video (actor performing lines)
2. [Text] → Voice Clone TTS → audio.wav
3. [Character Image] + driving.mp4 → LivePortrait → expression_video.mp4
4. expression_video.mp4 + audio.wav → Wav2Lip → lipsync.mp4
5. lipsync.mp4 → CodeFormer → final.mp4
```
Runtime and quality: benchmark the installed pipeline on the target footage.

## Troubleshooting

| Issue | Solution |
|-------|---------|
| Audio out of sync | Offset with ffmpeg: `ffmpeg -itsoffset 0.1 -i audio.wav ...` |
| Subtle mouth movements | Use wav2lip_gan.pth, increase audio volume |
| Face artifacts | Post-process with CodeFormer (fidelity 0.6-0.8) |
| Robotic voice clone | Use longer/cleaner reference, increase exaggeration |
| Unnatural head movement | Lower SadTalker pose_style to 0-10 |

## Reference

- `references/voice-synthesis.md` - Full voice tool documentation
- `references/models.md` - Voice model download links
- Character voice profiles in `projects/{project}/characters/`
