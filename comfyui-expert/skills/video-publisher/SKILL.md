---
name: video-publisher
description: Prepare and publish assembled videos to a user-selected platform. Route to installed publishing integrations when available; otherwise produce a validated metadata and delivery handoff. Use when a finished video is ready for distribution.
---

# Video Publisher

Thin orchestrator that routes to verified publishing capabilities or produces a complete
metadata and upload handoff itself.

Current target-platform requirements and the assembled output outrank every example in
this skill. Never imply an uploader or platform integration exists without verifying it.

## Publishing Workflow

```
PUBLISH REQUEST
    |
    |-- Need to plan content first?
    |   |-- Available research skill → Research competitors and gaps
    |   |-- Available planning skill → Generate title, thumbnail, hook
    |   |-- Available strategy skill → Optimize for discovery
    |
    |-- Ready to upload?
    |   |-- Verify video file is ready (video-assembly checklist passed)
    |   |-- Generate metadata (title, description, tags)
    |   |-- Verified uploader integration → Upload with metadata
    |
    |-- Post-publish?
    |   |-- Verified analytics integration → Monitor analytics
    |   |-- Track performance for future optimization
```

## Capability Delegation

Discover available runner skills and integrations before routing. If no matching
integration exists, produce the plan, metadata, thumbnail brief, and upload handoff
inside this skill; report upload itself as unavailable.

### Content Planning

| Task | Delegate To | Input |
|------|-------------|-------|
| Research topic viability | Available current-research capability | Topic/niche |
| Plan title + thumbnail + hook | Available content-planning capability | Research results |
| Optimize distribution | Available platform-strategy capability | Content plan |

### Upload

| Task | Delegate To | Input |
|------|-------------|-------|
| Upload video file | Verified uploader integration | Video file + metadata |
| Manage channel | Verified platform integration | Channel operations |

### Analytics

| Task | Delegate To | Input |
|------|-------------|-------|
| View performance | Verified analytics integration | Video/channel ID |
| Analyze for improvements | Available video-analysis capability | Video URL |

## Metadata Generation

When preparing to publish, generate:

### Title
- Use an installed title-optimization skill when available; otherwise draft directly
- Keep under 60 characters
- Include primary keyword
- Create curiosity gap

### Description
```
{Hook paragraph - what viewer will learn/see}

{Detailed description with timestamps}

{Links to resources mentioned}

{Social links and subscribe CTA}

---
Tags: {comma-separated relevant tags}
```

### Tags
- Primary topic keyword
- Related keywords
- Tool/software names (ComfyUI, Stable Diffusion, etc.)
- Technique names
- "AI video generation", "AI art tutorial", etc.

### Thumbnail
- Use an installed thumbnail-planning skill when available; otherwise produce a brief
- Character close-up or dramatic before/after
- Bold text overlay (3-5 words max)
- High contrast, readable at small size

## Platform-Specific Settings

### YouTube

| Setting | Recommended |
|---------|-------------|
| Resolution | 1920x1080 or 3840x2160 |
| Format | MP4 (H.264) |
| Frame rate | 24, 30, or 60 fps |
| Audio | AAC, 192kbps+ |
| Aspect ratio | 16:9 |

### YouTube Shorts

| Setting | Recommended |
|---------|-------------|
| Resolution | 1080x1920 (9:16) |
| Format | MP4 (H.264) |

### Instagram Reels

| Setting | Recommended |
|---------|-------------|
| Resolution | 1080x1920 (9:16) |
| Format | MP4 (H.264) |

### TikTok

| Setting | Recommended |
|---------|-------------|
| Resolution | 1080x1920 (9:16) |
| Format | MP4 (H.264) |

## Pre-Publish Checklist

- [ ] Video passes quality check (video-assembly checklist)
- [ ] Title optimized for search + curiosity
- [ ] Description includes timestamps and links
- [ ] Tags are relevant and comprehensive
- [ ] Thumbnail is compelling and readable at small size
- [ ] Category and audience settings are correct
- [ ] Schedule matches the active distribution plan
- [ ] End screen and cards planned
- [ ] Subtitles/CC file ready (if applicable)

## Integration

This skill is the final step in the VideoAgent pipeline:
```
Research → Plan → Generate → Assemble → Publish
```

It bridges the ComfyUI production pipeline with the YouTube publishing pipeline.
