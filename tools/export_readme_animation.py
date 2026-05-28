from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame
from PIL import Image

from double_integrator_pygame.app import Problem6App


OUTPUT = Path("docs/problem6_animation.gif")
FRAME_COUNT = 72
FRAME_MS = 55


def surface_to_image(surface: pygame.Surface) -> Image.Image:
    data = pygame.image.tostring(surface, "RGB")
    return Image.frombytes("RGB", surface.get_size(), data)


def main() -> None:
    app = Problem6App()
    app.playing = False
    app.speed = 1.0
    frames: list[Image.Image] = []

    for index in range(FRAME_COUNT):
        phase = index / (FRAME_COUNT - 1)
        app.elapsed = app.solution.tf * phase
        app.draw()
        image = surface_to_image(app.screen)
        frames.append(image.resize((820, 528), Image.Resampling.LANCZOS))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
    )
    pygame.quit()
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
