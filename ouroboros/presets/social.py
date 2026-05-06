"""
Social Media Presets — Quick presets for common video formats.
"""

from ouroboros.core.composition import Composition


def youtube_1080p(**kwargs) -> Composition:
    """YouTube 1080p preset: 1920x1080 @ 30fps."""
    return Composition(1920, 1080, 30, **kwargs)


def youtube_4k(**kwargs) -> Composition:
    """YouTube 4K preset: 3840x2160 @ 30fps."""
    return Composition(3840, 2160, 30, **kwargs)


def youtube_short(**kwargs) -> Composition:
    """YouTube Shorts: 1080x1920 @ 30fps."""
    return Composition(1080, 1920, 30, **kwargs)


def instagram_square(**kwargs) -> Composition:
    """Instagram Square: 1080x1080 @ 30fps."""
    return Composition(1080, 1080, 30, **kwargs)


def instagram_story(**kwargs) -> Composition:
    """Instagram Story: 1080x1920 @ 30fps."""
    return Composition(1080, 1920, 30, **kwargs)


def tiktok(**kwargs) -> Composition:
    """TikTok: 1080x1920 @ 30fps."""
    return Composition(1080, 1920, 30, **kwargs)


def twitter(**kwargs) -> Composition:
    """Twitter/X: 1280x720 @ 30fps."""
    return Composition(1280, 720, 30, **kwargs)


def facebook(**kwargs) -> Composition:
    """Facebook: 1280x720 @ 30fps."""
    return Composition(1280, 720, 30, **kwargs)


def linkedin(**kwargs) -> Composition:
    """LinkedIn: 1920x1080 @ 30fps."""
    return Composition(1920, 1080, 30, **kwargs)


def presentation(**kwargs) -> Composition:
    """Presentation: 1920x1080 @ 24fps."""
    return Composition(1920, 1080, 24, **kwargs)


def square(**kwargs) -> Composition:
    """Square video: 1080x1080 @ 30fps."""
    return Composition(1080, 1080, 30, **kwargs)


def vertical(**kwargs) -> Composition:
    """Vertical video: 1080x1920 @ 30fps."""
    return Composition(1080, 1920, 30, **kwargs)


def cinematic(**kwargs) -> Composition:
    """Cinematic: 2560x1080 (21:9) @ 24fps."""
    return Composition(2560, 1080, 24, **kwargs)


# Quick access dict
PRESETS = {
    "youtube-1080p": youtube_1080p,
    "youtube-4k": youtube_4k,
    "youtube-short": youtube_short,
    "instagram-square": instagram_square,
    "instagram-story": instagram_story,
    "tiktok": tiktok,
    "twitter": twitter,
    "facebook": facebook,
    "linkedin": linkedin,
    "presentation": presentation,
    "square": square,
    "vertical": vertical,
    "cinematic": cinematic,
}
