"""
Example: Hello World — Basic animated text.
"""

from ouroboros import *

comp = Composition(1920, 1080, 30)


@comp.scene(duration=5)
def intro(t):
    bg = Solid(color="#1a1a2e")
    title = Text("Hello Ouroboros 🐍", font_size=120, color="#e94560")
    subtitle = Text("The Ultimate Python Video Framework", font_size=40, color="#ffffff80")

    title.animate("opacity", 0, 1, 0, 0.5, ease_out)
    title.animate("y", 600, 400, 0, 1, ease_in_out)
    subtitle.animate("opacity", 0, 1, 0.3, 0.8, ease_out)

    return [bg, title, subtitle]


@comp.scene(duration=3)
def outro(t):
    bg = Solid(color="#0f3460")
    text = Text("Thanks for watching!", font_size=80, color="#e94560")
    text.animate("opacity", 0, 1, 0, 0.5, ease_out)
    text.animate("scale_x", 0.8, 1, 0, 1, ease_out_back)
    text.animate("scale_y", 0.8, 1, 0, 1, ease_out_back)
    return [bg, text]


if __name__ == "__main__":
    comp.render("hello_world.mp4")
