import json
import math
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


SOURCE = Path(r"C:\Users\Xuan\.codex\pets\plana\spritesheet.webp")
SOURCE_JSON = Path(r"C:\Users\Xuan\.codex\pets\plana\pet.json")
OUT = Path(r"C:\Users\Xuan\.codex\pets\clawd-plana")
ASSETS = OUT / "assets"
QA = OUT / "qa"
GEN_SRC = OUT / "source-generated"

CANVAS = (266, 200)
CELL = (192, 208)
FRAME_MS = 50

ROWS = {
    "idle": (0, 6),
    "running-right": (1, 8),
    "running-left": (2, 8),
    "waving": (3, 4),
    "jumping": (4, 5),
    "failed": (5, 8),
    "waiting": (6, 6),
    "running": (7, 6),
    "review": (8, 6),
}

MAIN_ASSETS = [
    ("plana-idle.apng", "idle", 48, "idle", 0.94, 1),
    ("plana-idle-look.apng", "waiting", 52, "look", 0.94, 1),
    ("plana-idle-reading.apng", "review", 64, "reading", 0.84, 2),
    ("plana-working-debugger.apng", "review", 64, "debugger", 0.84, 2),
    ("plana-yawning.apng", "waving", 64, "yawn", 0.90, 2),
    ("plana-dozing.apng", "waiting", 48, "doze", 0.92, 1),
    ("plana-collapsing.apng", "failed", 40, "collapse", 0.76, 1),
    ("plana-sleeping.apng", "idle", 64, "sleep", 0.74, 1),
    ("plana-waking.apng", "idle", 40, "wake", 0.76, 1),
    ("plana-thinking.apng", "review", 48, "thinking", 0.88, 2),
    ("plana-working-typing.apng", "review", 64, "typing", 0.84, 3),
    ("plana-working-building.apng", "jumping", 48, "building", 0.82, 3),
    ("plana-working-juggling.apng", "running", 48, "juggling", 0.84, 3),
    ("plana-working-conducting.apng", "waving", 48, "conducting", 0.84, 3),
    ("plana-working-sweeping.apng", "running-left", 48, "sweeping", 0.82, 3),
    ("plana-working-carrying.apng", "running-right", 48, "carrying", 0.82, 3),
    ("plana-error.apng", "failed", 40, "error", 0.90, 2),
    ("plana-happy.apng", "jumping", 48, "happy", 0.90, 2),
    ("plana-notification.apng", "waving", 40, "notification", 0.90, 2),
    ("plana-react-drag.apng", "running", 32, "drag", 0.88, 2),
    ("plana-react-left.apng", "waving", 40, "react-left", 0.90, 2),
    ("plana-react-right.apng", "waving", 40, "react-right", 0.90, 2),
    ("plana-react-annoyed.apng", "failed", 40, "annoyed", 0.90, 2),
    ("plana-react-double.apng", "jumping", 44, "double", 0.90, 2),
    ("plana-react-double-jump.apng", "jumping", 44, "double-jump", 0.90, 3),
]

MINI_ASSETS = [
    ("plana-mini-idle.apng", "idle", 48, "mini-idle", 0.58, 1),
    ("plana-mini-alert.apng", "waving", 32, "mini-alert", 0.58, 2),
    ("plana-mini-happy.apng", "jumping", 40, "mini-happy", 0.58, 2),
    ("plana-mini-enter.apng", "running-right", 24, "mini-enter", 0.58, 2),
    ("plana-mini-peek.apng", "waiting", 18, "mini-peek", 0.58, 1),
    ("plana-mini-typing.apng", "review", 48, "mini-typing", 0.56, 3),
    ("plana-mini-crabwalk.apng", "running-left", 32, "mini-crabwalk", 0.56, 3),
    ("plana-mini-enter-sleep.apng", "idle", 24, "mini-enter-sleep", 0.56, 1),
    ("plana-mini-sleep.apng", "idle", 48, "mini-sleep", 0.56, 1),
]

GENERATED_ASSETS = {
    "plana-yawning.apng": ("sleep-reactions-grid.png", 6, 6, 0, 64, "main"),
    "plana-dozing.apng": ("sleep-reactions-grid.png", 6, 6, 1, 48, "main"),
    "plana-collapsing.apng": ("sleep-reactions-grid.png", 6, 6, 2, 40, "wide-sleep"),
    "plana-sleeping.apng": ("sleep-reactions-grid.png", 6, 6, 3, 64, "wide-sleep"),
    "plana-waking.apng": ("waking-strip.png", 6, 1, 0, 40, "wide-sleep"),
    "plana-notification.apng": ("sleep-reactions-grid.png", 6, 6, 5, 40, "main"),
    "plana-working-typing.apng": ("working-grid.png", 6, 6, 0, 64, "main-work"),
    "plana-working-building.apng": ("building-strip.png", 6, 1, 0, 48, "wide-work"),
    "plana-working-juggling.apng": ("juggling-strip.png", 6, 1, 0, 48, "main-work"),
    "plana-working-conducting.apng": ("conducting-strip.png", 6, 1, 0, 48, "main-work"),
    "plana-working-sweeping.apng": ("working-grid.png", 6, 6, 4, 48, "wide-work"),
    "plana-working-carrying.apng": ("carrying-strip.png", 6, 1, 0, 48, "wide-work"),
    "plana-mini-idle.apng": ("mini-grid.png", 6, 6, 0, 48, "mini"),
    "plana-mini-alert.apng": ("mini-grid.png", 6, 6, 1, 32, "mini"),
    "plana-mini-happy.apng": ("mini-grid.png", 6, 6, 2, 40, "mini"),
    "plana-mini-enter.apng": ("mini-grid.png", 6, 6, 3, 24, "mini"),
    "plana-mini-peek.apng": ("mini-grid.png", 6, 6, 4, 18, "mini-peek"),
    "plana-mini-typing.apng": ("mini-grid.png", 6, 6, 5, 48, "mini"),
    "plana-mini-crabwalk.apng": ("mini-grid.png", 6, 6, 3, 32, "mini"),
    "plana-mini-enter-sleep.apng": ("sleep-reactions-grid.png", 6, 6, 3, 24, "mini-sleep"),
    "plana-mini-sleep.apng": ("sleep-reactions-grid.png", 6, 6, 3, 48, "mini-sleep"),
}

STABILIZED_ATLAS_ASSETS = set(GENERATED_ASSETS)

GENERATED_CYCLES = {
    "plana-dozing.apng": 2,
    "plana-notification.apng": 3,
    "plana-working-typing.apng": 4,
    "plana-working-building.apng": 2,
    "plana-working-juggling.apng": 4,
    "plana-working-conducting.apng": 4,
    "plana-working-sweeping.apng": 4,
    "plana-working-carrying.apng": 4,
    "plana-mini-idle.apng": 2,
    "plana-mini-alert.apng": 3,
    "plana-mini-happy.apng": 3,
    "plana-mini-enter.apng": 2,
    "plana-mini-peek.apng": 1,
    "plana-mini-typing.apng": 4,
    "plana-mini-crabwalk.apng": 4,
    "plana-mini-enter-sleep.apng": 1,
    "plana-mini-sleep.apng": 1,
}

FIT = {
    "main": {"max": (156, 188), "center": (133, 194)},
    "main-work": {"max": (170, 188), "center": (128, 194)},
    "wide-work": {"max": (198, 184), "center": (128, 194)},
    "wide-sleep": {"max": (215, 150), "center": (133, 185)},
    "mini": {"max": (104, 132), "center": (133, 185)},
    "mini-peek": {"max": (104, 132), "center": (133, 198)},
    "mini-sleep": {"max": (128, 88), "center": (133, 186)},
}


def ensure_dirs() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)


def extract_rows() -> dict[str, list[Image.Image]]:
    atlas = Image.open(SOURCE).convert("RGBA")
    frames = {}
    for name, (row, count) in ROWS.items():
        row_frames = []
        for col in range(count):
            x = col * CELL[0]
            y = row * CELL[1]
            row_frames.append(atlas.crop((x, y, x + CELL[0], y + CELL[1])))
        frames[name] = row_frames
    return frames


def ease(value: float) -> float:
    return 0.5 - math.cos(value * math.pi) * 0.5


def sprite_from_cell(
    cell: Image.Image,
    scale: float,
    angle: float = 0,
    crop: bool = False,
    flip: bool = False,
) -> Image.Image:
    sprite = cell.crop(cell.getbbox()) if crop and cell.getbbox() else cell.copy()
    if flip:
        sprite = ImageOps.mirror(sprite)
    size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
    sprite = sprite.resize(size, Image.Resampling.LANCZOS)
    if angle:
        sprite = sprite.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    return sprite


def paste_sprite(
    canvas: Image.Image,
    sprite: Image.Image,
    center_x: float,
    baseline: float,
    dx: float = 0,
    dy: float = 0,
) -> tuple[int, int, int, int]:
    x = round(center_x - sprite.width / 2 + dx)
    y = round(baseline - sprite.height + dy)
    canvas.alpha_composite(sprite, (x, y))
    return (x, y, x + sprite.width, y + sprite.height)


def draw_round_rect(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_prop(canvas: Image.Image, kind: str, phase: float) -> None:
    draw = ImageDraw.Draw(canvas)
    pulse = math.sin(phase * math.tau)

    if kind in {"typing", "mini-typing"}:
        if kind == "typing":
            x0, y0, screen_w, screen_h = 82, 137, 74, 34
        else:
            x0, y0, screen_w, screen_h = 113, 159, 45, 21
        draw_round_rect(draw, (x0 + 4, y0, x0 + 4 + screen_w, y0 + screen_h), 3, (20, 29, 43, 255), (8, 11, 18, 255), 2)
        draw.rectangle((x0 + 10, y0 + 7, x0 + screen_w - 6, y0 + screen_h - 8), fill=(32, 52, 73, 255))
        for i in range(3):
            yy = y0 + 10 + i * 6
            bright = 116 + ((i + round(phase * 8)) % 2) * 60
            draw.line((x0 + 14, yy, x0 + screen_w - 12 - i * 8, yy), fill=(bright, 211, 255, 255), width=2)
        base_y = y0 + screen_h
        draw.polygon(
            [(x0, base_y), (x0 + screen_w + 12, base_y), (x0 + screen_w + 20, base_y + 14), (x0 + 8, base_y + 14)],
            fill=(35, 43, 61, 255),
            outline=(8, 11, 18, 255),
        )
        key_cols = 8 if kind == "typing" else 5
        for row in range(2):
            for col in range(key_cols):
                bright = 132 + ((col + row + round(phase * 12)) % 3) * 30
                x = x0 + 10 + col * (7 if kind == "typing" else 6)
                y = base_y + 4 + row * 5
                draw.rectangle((x, y, x + 4, y + 2), fill=(bright, 218, 255, 255))

    elif kind in {"reading", "debugger", "thinking"}:
        x0 = 151 + round(pulse)
        y0 = 118 if kind != "thinking" else 130
        draw_round_rect(draw, (x0, y0, x0 + 70, y0 + 45), 4, (23, 29, 43, 235), (7, 10, 16, 255), 2)
        color = (128, 215, 255, 255) if kind != "thinking" else (255, 92, 132, 255)
        for i in range(5):
            yy = y0 + 10 + i * 6
            draw.line((x0 + 9, yy, x0 + 54 - (i % 2) * 14, yy), fill=color, width=2)

    elif kind == "building":
        colors = [(65, 142, 255, 255), (255, 92, 132, 255), (255, 210, 91, 255)]
        base_x, base_y = 164, 164
        lift = round(abs(math.sin(phase * math.tau * 2)) * 7)
        for i in range(5):
            x = base_x + (i % 3) * 18
            y = base_y - (i // 3) * 18 - (lift if i == round(phase * 5) % 5 else 0)
            draw.rectangle((x, y, x + 17, y + 17), fill=colors[i % 3], outline=(18, 22, 31, 255), width=2)

    elif kind == "juggling":
        cx, cy = 178, 120
        colors = [(255, 92, 132, 255), (86, 205, 255, 255), (255, 219, 98, 255)]
        for i in range(3):
            a = phase * math.tau + i * math.tau / 3
            x = cx + math.cos(a) * 32
            y = cy + math.sin(a) * 19
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=colors[i], outline=(15, 18, 26, 255), width=2)

    elif kind == "conducting":
        x0, y0 = 151, 126
        x1 = 208 + math.sin(phase * math.tau * 2) * 4
        y1 = 100 + math.cos(phase * math.tau * 2) * 8
        draw.line((x0, y0, x1, y1), fill=(242, 229, 194, 255), width=4)
        draw.line((x0, y0, x1, y1), fill=(76, 52, 43, 255), width=1)

    elif kind == "sweeping":
        x0 = 144 + math.sin(phase * math.tau * 2) * 3
        draw.line((x0, 126, x0 + 48, 184), fill=(111, 74, 44, 255), width=5)
        draw.polygon(
            [(x0 + 40, 174), (x0 + 66, 188), (x0 + 52, 196), (x0 + 31, 181)],
            fill=(79, 164, 230, 255),
            outline=(15, 19, 28, 255),
        )

    elif kind == "carrying":
        x0 = 126 + round(math.sin(phase * math.tau * 2) * 1)
        y0 = 143 + round(abs(math.sin(phase * math.tau)) * 2)
        draw_round_rect(draw, (x0, y0, x0 + 48, y0 + 38), 2, (158, 112, 67, 255), (39, 29, 22, 255), 3)
        draw.line((x0, y0 + 14, x0 + 48, y0 + 14), fill=(120, 82, 48, 255), width=2)
        draw.line((x0 + 24, y0, x0 + 24, y0 + 38), fill=(120, 82, 48, 255), width=2)
        draw.arc((x0 + 14, y0 + 7, x0 + 34, y0 + 22), 200, 340, fill=(60, 43, 29, 255), width=2)

    elif kind in {"notification", "mini-alert"}:
        x, y = 184, 36 if kind == "notification" else 150
        r = 13 + round(abs(pulse) * 2)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 74, 106, 255), outline=(39, 12, 22, 255), width=3)
        draw.line((x, y - 7, x, y + 3), fill=(255, 245, 247, 255), width=3)
        draw.point((x, y + 8), fill=(255, 245, 247, 255))

    elif kind in {"error", "annoyed"}:
        x = 176 + round(math.sin(phase * math.tau * 3) * 3)
        y = 52
        draw.line((x - 8, y, x + 8, y + 15), fill=(255, 69, 97, 255), width=4)
        draw.line((x + 8, y, x - 8, y + 15), fill=(255, 69, 97, 255), width=4)
        if kind == "annoyed":
            for i in range(3):
                yy = 76 + i * 7
                draw.line((184, yy, 204, yy - 4), fill=(255, 84, 105, 255), width=3)

    elif kind in {"happy", "double", "double-jump", "mini-happy"}:
        x, y = (182, 48) if not kind.startswith("mini") else (163, 144)
        for i in range(4):
            a = phase * math.tau + i * math.tau / 4
            px = x + math.cos(a) * 18
            py = y + math.sin(a) * 10
            draw.polygon(
                [(px, py - 5), (px + 4, py), (px, py + 5), (px - 4, py)],
                fill=(255, 218, 91, 255),
                outline=(56, 37, 16, 255),
            )

    elif kind in {"sleep", "mini-sleep", "mini-enter-sleep"}:
        x, y = (181, 117) if kind == "sleep" else (161, 155)
        for i in range(3):
            rr = 4 + i
            px = x + i * 11 + round(math.sin(phase * math.tau + i) * 2)
            py = y - i * 12 - round((phase * 8 + i * 2) % 8)
            draw.polygon(
                [(px, py - rr), (px + rr, py), (px, py + rr), (px - rr, py)],
                fill=(132, 206, 255, 220),
                outline=(25, 42, 66, 230),
            )


def motion(kind: str, phase: float) -> dict[str, float | bool]:
    wave = math.sin(phase * math.tau)
    wave2 = math.sin(phase * math.tau * 2)
    params: dict[str, float | bool] = {
        "dx": 0,
        "dy": 0,
        "angle": 0,
        "baseline": 197,
        "center_x": 124 if kind in {"typing", "reading", "debugger", "thinking"} else 133,
        "crop": False,
        "flip": False,
    }

    if kind in {"idle", "look", "doze"}:
        params["dy"] = wave * 2
        params["angle"] = wave * (1.5 if kind == "look" else 0.7)
    elif kind in {"yawn", "react-left", "react-right"}:
        params["dy"] = -abs(wave) * 4
        params["angle"] = wave * (4 if kind != "react-right" else -4)
        params["dx"] = -5 if kind == "react-left" else 5 if kind == "react-right" else 0
    elif kind in {"happy", "double", "double-jump"}:
        params["dy"] = -abs(wave2) * (9 if kind != "double-jump" else 15)
        params["angle"] = wave * 5
    elif kind == "collapse":
        p = ease(min(1, phase * 1.2))
        params.update({"crop": True, "angle": p * 84, "baseline": 190, "dy": p * 8, "center_x": 136})
    elif kind == "sleep":
        params.update({"crop": True, "angle": 84 + wave * 1.5, "baseline": 190, "center_x": 136, "dy": wave * 1})
    elif kind == "wake":
        p = 1 - ease(min(1, phase * 1.35))
        params.update({"crop": True, "angle": p * 84, "baseline": 190, "dy": p * 8, "center_x": 136})
    elif kind in {"error", "annoyed"}:
        params["dx"] = math.sin(phase * math.tau * 9) * 3
        params["angle"] = wave2 * 3
    elif kind == "drag":
        params["angle"] = 8 + wave * 4
        params["dx"] = wave2 * 5
    elif kind in {"building", "juggling", "conducting", "sweeping", "carrying"}:
        params["dy"] = wave2 * 1.2
        params["angle"] = wave * 1.2
        params["center_x"] = 119 if kind in {"sweeping", "carrying"} else 124
    elif kind == "notification":
        params["dy"] = wave2 * 3
        params["angle"] = wave * 3
    elif kind.startswith("mini"):
        params.update({"baseline": 188, "center_x": 128})
        if kind in {"mini-enter", "mini-crabwalk"}:
            params["dx"] = math.sin(phase * math.tau * 2) * 8
        if kind == "mini-peek":
            p = math.sin(phase * math.pi)
            params["dy"] = 36 - p * 28
        elif kind in {"mini-enter-sleep", "mini-sleep"}:
            params.update({"crop": True, "angle": 83, "center_x": 132, "baseline": 188})
        else:
            params["dy"] = wave * 2
    return params


def render_frame(cell: Image.Image, kind: str, scale: float, phase: float, include_prop: bool = True) -> Image.Image:
    params = motion(kind, phase)
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    sprite = sprite_from_cell(
        cell,
        scale=scale,
        angle=float(params["angle"]),
        crop=bool(params["crop"]),
        flip=bool(params["flip"]),
    )
    paste_sprite(
        canvas,
        sprite,
        center_x=float(params["center_x"]),
        baseline=float(params["baseline"]),
        dx=float(params["dx"]),
        dy=float(params["dy"]),
    )
    if include_prop:
        draw_prop(canvas, kind, phase)
    return canvas


def build_sequence(row_frames: list[Image.Image], count: int, kind: str, scale: float, loops: int) -> list[Image.Image]:
    frames = []
    for i in range(count):
        phase = i / count
        position = phase * len(row_frames) * loops
        source_idx = math.floor(position) % len(row_frames)
        frac = position - math.floor(position)
        current = render_frame(row_frames[source_idx], kind, scale, phase, include_prop=False)
        next_frame = render_frame(row_frames[(source_idx + 1) % len(row_frames)], kind, scale, phase, include_prop=False)
        frame = blended_frame(current, next_frame, frac)
        draw_prop(frame, kind, phase)
        frames.append(frame)
    return frames


def is_key_color(pixel: tuple[int, int, int, int]) -> bool:
    r, g, b, a = pixel
    return a > 0 and g > 80 and g - max(r, b) > 16 and g > min(r, b) * 1.12


def remove_connected_green(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size
    stack = []
    seen = set()
    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= width or y >= height or (x, y) in seen:
            continue
        if not is_key_color(pixels[x, y]):
            continue
        seen.add((x, y))
        pixels[x, y] = (0, 0, 0, 0)
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    return image


def despill_green_edges(image: Image.Image) -> Image.Image:
    arr = np.array(image.convert("RGBA"))
    alpha = arr[:, :, 3]
    if not np.any(alpha):
        return image

    opaque_mask = (alpha > 0).astype(np.uint8)
    distance = cv2.distanceTransform(opaque_mask, cv2.DIST_L2, 3)
    rgb = arr[:, :, :3].astype(np.int16)
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    dominance = green - np.maximum(red, blue)
    near_edge = (alpha > 0) & (distance <= 3.25)
    spill = near_edge & (green > 72) & (dominance > 10)

    if np.any(spill):
        strength = np.clip((dominance.astype(np.float32) - 10.0) / 90.0, 0.0, 0.92)
        edge_strength = np.clip((3.25 - distance.astype(np.float32)) / 3.25, 0.0, 1.0)
        reduction = 1.0 - strength * edge_strength * 0.92
        new_alpha = alpha.astype(np.float32) * reduction
        alpha[spill] = np.clip(new_alpha[spill], 0, 255).astype(np.uint8)
        cap = np.maximum(red, blue) + 2
        arr[:, :, 1][spill] = np.minimum(arr[:, :, 1][spill], cap[spill]).astype(np.uint8)

    arr[:, :, 3] = alpha
    return Image.fromarray(arr, "RGBA")


def normalized_generated_frame(cell: Image.Image, fit_name: str, phase: float) -> Image.Image:
    cleaned = despill_green_edges(remove_connected_green(cell))
    bbox = cleaned.getbbox()
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    if not bbox:
        return canvas

    sprite = cleaned.crop(bbox)
    cfg = FIT[fit_name]
    max_w, max_h = cfg["max"]
    center_x, baseline = cfg["center"]
    if fit_name in {"main-work", "wide-work", "mini"}:
        scale = min(max_h / sprite.height, (CANVAS[0] - 8) / sprite.width)
    else:
        scale = min(max_w / sprite.width, max_h / sprite.height)
    size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
    sprite = sprite.resize(size, Image.Resampling.LANCZOS)
    bob = math.sin(phase * math.tau) * (1.5 if "sleep" not in fit_name else 0.5)
    x = round(center_x - sprite.width / 2)
    y = round(baseline - sprite.height + bob)
    canvas.alpha_composite(sprite, (x, y))
    return canvas


def component_cells(sheet: Image.Image, columns: int, rows: int) -> dict[tuple[int, int], Image.Image]:
    arr = np.array(sheet.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.float32)
    alpha = arr[:, :, 3]
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    key = (
        (alpha > 0)
        & (green > 80)
        & ((green - np.maximum(red, blue)) > 16)
        & (green > np.minimum(red, blue) * 1.12)
    )

    _, key_labels = cv2.connectedComponents(key.astype(np.uint8), connectivity=8)
    border_labels = set(np.unique(key_labels[0, :]))
    border_labels.update(np.unique(key_labels[-1, :]))
    border_labels.update(np.unique(key_labels[:, 0]))
    border_labels.update(np.unique(key_labels[:, -1]))
    background = key & np.isin(key_labels, list(border_labels))

    clean = arr.copy()
    clean[background, 3] = 0
    foreground = clean[:, :, 3] > 0
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(foreground.astype(np.uint8), connectivity=8)

    components = []
    height, width = foreground.shape
    for label in range(1, count):
        x, y, w, h, area = stats[label]
        if area < 80:
            continue
        cx, cy = centroids[label]
        row = min(rows - 1, max(0, int(cy / (height / rows))))
        components.append(
            {
                "label": label,
                "box": (x, y, x + w, y + h),
                "area": int(area),
                "center": (float(cx), float(cy)),
                "row": row,
                "w": int(w),
                "h": int(h),
            }
        )

    row_centers: dict[int, list[float]] = {}
    for row_idx in range(rows):
        row_components = [c for c in components if c["row"] == row_idx]
        body_components = [
            c
            for c in row_components
            if c["area"] > 900 and c["w"] > width / (columns * 9) and c["h"] > height / (rows * 8)
        ]
        if len(body_components) >= columns:
            selected = sorted(body_components, key=lambda c: c["area"], reverse=True)[:columns]
            row_centers[row_idx] = [c["center"][0] for c in sorted(selected, key=lambda c: c["center"][0])]

    grouped: dict[tuple[int, int], list[tuple[int, tuple[int, int, int, int]]]] = {}
    for component in components:
        row = int(component["row"])
        cx = component["center"][0]
        centers = row_centers.get(row)
        if centers:
            col = min(range(len(centers)), key=lambda idx: abs(cx - centers[idx]))
        else:
            col = min(columns - 1, max(0, int(cx / (width / columns))))
        grouped.setdefault((row, col), []).append((int(component["label"]), component["box"]))

    cells: dict[tuple[int, int], Image.Image] = {}
    for key_pos, components in grouped.items():
        x1 = min(box[0] for _, box in components)
        y1 = min(box[1] for _, box in components)
        x2 = max(box[2] for _, box in components)
        y2 = max(box[3] for _, box in components)
        cell_arr = np.zeros((y2 - y1, x2 - x1, 4), dtype=np.uint8)
        for label, (bx1, by1, bx2, by2) in components:
            piece = clean[by1:by2, bx1:bx2].copy()
            mask = labels[by1:by2, bx1:bx2] == label
            piece[~mask, 3] = 0
            px1 = bx1 - x1
            py1 = by1 - y1
            alpha_piece = piece[:, :, 3:4].astype(np.float32) / 255.0
            target = cell_arr[py1 : py1 + piece.shape[0], px1 : px1 + piece.shape[1]].astype(np.float32)
            source = piece.astype(np.float32)
            out_alpha = alpha_piece + target[:, :, 3:4] / 255.0 * (1.0 - alpha_piece)
            out_rgb = source[:, :, :3] * alpha_piece + target[:, :, :3] * (1.0 - alpha_piece)
            target[:, :, :3] = out_rgb
            target[:, :, 3:4] = out_alpha * 255.0
            cell_arr[py1 : py1 + piece.shape[0], px1 : px1 + piece.shape[1]] = np.clip(target, 0, 255).astype(np.uint8)
        cells[key_pos] = Image.fromarray(cell_arr, "RGBA")
    return cells


def generated_keyframes(source_name: str, columns: int, rows: int, row: int, fit_name: str) -> list[Image.Image]:
    path = GEN_SRC / source_name
    if not path.exists():
        raise FileNotFoundError(f"generated source is missing: {path}")
    sheet = Image.open(path).convert("RGBA")
    grouped = component_cells(sheet, columns, rows)
    cell_w = sheet.width / columns
    cell_h = sheet.height / rows
    frames = []
    for col in range(columns):
        box = (round(col * cell_w), round(row * cell_h), round((col + 1) * cell_w), round((row + 1) * cell_h))
        cell = grouped.get((row, col), sheet.crop(box))
        phase = col / columns
        frames.append(normalized_generated_frame(cell, fit_name, phase))
    return frames


def boosted_count(count: int) -> int:
    return max(count, int(math.ceil(count * 62 / FRAME_MS / 2)) * 2)


_FLOW_CACHE: dict[tuple[int, int], tuple[np.ndarray, np.ndarray]] = {}


def flow_gray(image: Image.Image) -> np.ndarray:
    arr = np.array(image.convert("RGBA"), dtype=np.float32)
    alpha = arr[:, :, 3] / 255.0
    luminance = arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114
    gray = luminance * alpha + 255.0 * (1.0 - alpha)
    return np.clip(gray * 0.45 + alpha * 255.0 * 0.55, 0, 255).astype(np.uint8)


def optical_flow_pair(a: Image.Image, b: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    key = (id(a), id(b))
    cached = _FLOW_CACHE.get(key)
    if cached is not None:
        return cached
    gray_a = flow_gray(a)
    gray_b = flow_gray(b)
    flow_ab = cv2.calcOpticalFlowFarneback(gray_a, gray_b, None, 0.5, 3, 21, 3, 5, 1.2, 0)
    flow_ba = cv2.calcOpticalFlowFarneback(gray_b, gray_a, None, 0.5, 3, 21, 3, 5, 1.2, 0)
    _FLOW_CACHE[key] = (flow_ab, flow_ba)
    return flow_ab, flow_ba


def premultiplied_array(image: Image.Image) -> np.ndarray:
    arr = np.array(image.convert("RGBA"), dtype=np.float32) / 255.0
    arr[:, :, :3] *= arr[:, :, 3:4]
    return arr


def warp_array(arr: np.ndarray, flow: np.ndarray, amount: float) -> np.ndarray:
    height, width = arr.shape[:2]
    grid_x, grid_y = np.meshgrid(np.arange(width), np.arange(height))
    map_x = (grid_x - flow[:, :, 0] * amount).astype(np.float32)
    map_y = (grid_y - flow[:, :, 1] * amount).astype(np.float32)
    return cv2.remap(arr, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def blended_frame(a: Image.Image, b: Image.Image, amount: float) -> Image.Image:
    amount = ease(max(0.0, min(1.0, amount)))
    if amount <= 0.001:
        return a
    if amount >= 0.999:
        return b
    flow_ab, flow_ba = optical_flow_pair(a, b)
    if amount <= 0.5:
        out = warp_array(premultiplied_array(a), flow_ab, amount)
    else:
        out = warp_array(premultiplied_array(b), flow_ba, 1.0 - amount)
    out_alpha = out[:, :, 3:4]
    out_rgb = out[:, :, :3]
    with np.errstate(divide="ignore", invalid="ignore"):
        out_rgb = np.where(out_alpha > 0, out_rgb / np.maximum(out_alpha, 1e-6), 0)
    rgba = np.dstack([out_rgb, out_alpha])
    return Image.fromarray(np.clip(rgba * 255.0, 0, 255).astype(np.uint8), "RGBA")


def build_generated_sequence(filename: str, count: int) -> list[Image.Image]:
    source_name, columns, rows, row, _base_count, fit_name = GENERATED_ASSETS[filename]
    keyframes = generated_keyframes(source_name, columns, rows, row, fit_name)
    cycles = GENERATED_CYCLES.get(filename, 1)
    if len(keyframes) < 2:
        return keyframes * count

    frames = []
    for i in range(count):
        if cycles == 1:
            position = (i / max(1, count - 1)) * (len(keyframes) - 1)
            idx = min(len(keyframes) - 2, math.floor(position))
            frac = position - idx
            frame = blended_frame(keyframes[idx], keyframes[idx + 1], frac)
        else:
            position = (i / count) * len(keyframes) * cycles
            idx = math.floor(position) % len(keyframes)
            frac = position - math.floor(position)
            frame = blended_frame(keyframes[idx], keyframes[(idx + 1) % len(keyframes)], frac)
        t = i / count
        if fit_name == "mini":
            dx = round(math.sin(t * math.tau * cycles) * 1)
            dy = round(math.sin(t * math.tau * max(1, cycles // 2)) * 1)
            shifted = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
            shifted.alpha_composite(frame, (dx, dy))
            frame = shifted
        frames.append(frame)
    return frames


def save_apng(path: Path, frames: list[Image.Image]) -> None:
    encoded = []
    for idx, frame in enumerate(frames):
        marked = frame.copy()
        marked.putpixel((0, 0), ((idx * 17) % 256, (idx * 47) % 256, (idx * 83) % 256, 0))
        marked.putpixel((CANVAS[0] - 1, CANVAS[1] - 1), ((idx * 23) % 256, (idx * 61) % 256, (idx * 97) % 256, 0))
        encoded.append(marked)
    encoded[0].save(
        path,
        format="PNG",
        save_all=True,
        append_images=encoded[1:],
        duration=FRAME_MS,
        loop=0,
        disposal=2,
        blend=0,
        optimize=False,
    )


def create_assets(rows: dict[str, list[Image.Image]]) -> tuple[dict[str, dict[str, object]], dict[str, list[Image.Image]]]:
    report = {}
    previews = {}
    for filename, row, count, kind, scale, loops in MAIN_ASSETS + MINI_ASSETS:
        frame_count = boosted_count(count)
        if filename in GENERATED_ASSETS and filename not in STABILIZED_ATLAS_ASSETS:
            frames = build_generated_sequence(filename, frame_count)
            source = f"generated:{GENERATED_ASSETS[filename][0]}"
            source_row = GENERATED_ASSETS[filename][3]
        else:
            frames = build_sequence(rows[row], frame_count, kind, scale, loops)
            source = "atlas"
            source_row = row
        save_apng(ASSETS / filename, frames)
        report[filename] = {
            "source": source,
            "sourceRow": source_row,
            "frames": frame_count,
            "durationMs": FRAME_MS,
            "fps": round(1000 / FRAME_MS, 2),
            "size": CANVAS,
        }
        previews[filename] = frames
    return report, previews


def theme_json() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "name": "Clawd Plana",
        "author": "Xuan",
        "version": "1.1.2",
        "description": "Plana converted into a high-frame, cleaned-edge APNG Clawd on Desk theme.",
        "viewBox": {"x": 0, "y": 0, "width": CANVAS[0], "height": CANVAS[1]},
        "layout": {
            "contentBox": {"x": 48, "y": 4, "width": 154, "height": 190},
            "marginBox": {"x": 36, "y": 0, "width": 194, "height": 200},
            "centerX": 133,
            "baselineY": 194,
            "visibleHeightRatio": 0.56,
            "baselineBottomRatio": 0.04,
        },
        "eyeTracking": {"enabled": False, "states": []},
        "states": {
            "idle": ["plana-idle.apng"],
            "yawning": ["plana-yawning.apng"],
            "dozing": ["plana-dozing.apng"],
            "collapsing": ["plana-collapsing.apng"],
            "thinking": ["plana-thinking.apng"],
            "working": ["plana-working-typing.apng"],
            "juggling": ["plana-working-juggling.apng"],
            "sweeping": ["plana-working-sweeping.apng"],
            "error": ["plana-error.apng"],
            "attention": ["plana-happy.apng"],
            "notification": ["plana-notification.apng"],
            "carrying": ["plana-working-carrying.apng"],
            "sleeping": ["plana-sleeping.apng"],
            "waking": ["plana-waking.apng"],
        },
        "sleepSequence": {"mode": "full"},
        "workingTiers": [
            {"minSessions": 3, "file": "plana-working-building.apng"},
            {"minSessions": 2, "file": "plana-working-juggling.apng"},
            {"minSessions": 1, "file": "plana-working-typing.apng"},
        ],
        "jugglingTiers": [
            {"minSessions": 2, "file": "plana-working-conducting.apng"},
            {"minSessions": 1, "file": "plana-working-juggling.apng"},
        ],
        "idleAnimations": [
            {"file": "plana-idle-look.apng", "duration": 5200},
            {"file": "plana-idle-reading.apng", "duration": 6500},
            {"file": "plana-working-debugger.apng", "duration": 6500},
        ],
        "displayHintMap": {
            "clawd-working-building.svg": "plana-working-building.apng",
            "clawd-working-typing.svg": "plana-working-typing.apng",
            "clawd-working-juggling.svg": "plana-working-juggling.apng",
            "clawd-working-conducting.svg": "plana-working-conducting.apng",
            "clawd-idle-reading.svg": "plana-idle-reading.apng",
            "clawd-working-debugger.svg": "plana-working-debugger.apng",
            "clawd-working-thinking.svg": "plana-thinking.apng",
        },
        "updateVisuals": {"checking": "plana-working-debugger.apng"},
        "timings": {
            "minDisplay": {
                "attention": 4000,
                "error": 5000,
                "sweeping": 5500,
                "notification": 3000,
                "carrying": 3000,
                "working": 1000,
                "thinking": 1000,
            },
            "autoReturn": {
                "attention": 4000,
                "error": 5000,
                "sweeping": 300000,
                "notification": 3000,
                "carrying": 3000,
            },
            "yawnDuration": 4000,
            "collapseDuration": 2500,
            "wakeDuration": 2500,
            "deepSleepTimeout": 600000,
            "mouseIdleTimeout": 20000,
            "mouseSleepTimeout": 60000,
        },
        "hitBoxes": {
            "default": {"x": 70, "y": 12, "w": 125, "h": 176},
            "sleeping": {"x": 54, "y": 92, "w": 160, "h": 82},
            "wide": {"x": 44, "y": 18, "w": 180, "h": 170},
        },
        "wideHitboxFiles": [
            "plana-error.apng",
            "plana-notification.apng",
            "plana-working-conducting.apng",
            "plana-working-sweeping.apng",
            "plana-working-carrying.apng",
            "plana-working-building.apng",
            "plana-working-juggling.apng",
        ],
        "sleepingHitboxFiles": [
            "plana-collapsing.apng",
            "plana-sleeping.apng",
            "plana-waking.apng",
        ],
        "reactions": {
            "drag": {"file": "plana-react-drag.apng"},
            "clickLeft": {"file": "plana-react-left.apng", "duration": 2500},
            "clickRight": {"file": "plana-react-right.apng", "duration": 2500},
            "annoyed": {"file": "plana-react-annoyed.apng", "duration": 3500},
            "double": {
                "files": ["plana-react-double.apng", "plana-react-double-jump.apng"],
                "duration": 3500,
            },
        },
        "miniMode": {
            "supported": True,
            "flipAssets": True,
            "offsetRatio": 0.486,
            "states": {
                "mini-idle": ["plana-mini-idle.apng"],
                "mini-alert": ["plana-mini-alert.apng"],
                "mini-happy": ["plana-mini-happy.apng"],
                "mini-enter": ["plana-mini-enter.apng"],
                "mini-peek": ["plana-mini-peek.apng"],
                "mini-working": ["plana-mini-typing.apng"],
                "mini-crabwalk": ["plana-mini-crabwalk.apng"],
                "mini-enter-sleep": ["plana-mini-enter-sleep.apng"],
                "mini-sleep": ["plana-mini-sleep.apng"],
            },
            "timings": {
                "minDisplay": {"mini-alert": 4000, "mini-happy": 4000, "mini-peek": 1500},
                "autoReturn": {"mini-alert": 4000, "mini-happy": 4000, "mini-peek": 1500},
            },
            "glyphFlips": {},
        },
        "objectScale": {
            "widthRatio": 0.62,
            "heightRatio": 0.58,
            "imgWidthRatio": 0.62,
            "objBottom": 0.05,
            "imgBottom": 0.05,
            "offsetX": 0.0,
            "offsetY": 0.0,
            "fileScales": {
                "plana-working-typing.apng": 1.05,
                "plana-working-building.apng": 1.05,
                "plana-working-juggling.apng": 1.05,
                "plana-working-conducting.apng": 1.05,
                "plana-working-sweeping.apng": 1.08,
                "plana-working-carrying.apng": 1.08,
                "plana-error.apng": 1.04,
                "plana-happy.apng": 1.04,
                "plana-thinking.apng": 1.04,
            },
            "fileOffsets": {
                "plana-working-typing.apng": {"x": -6, "y": 0},
                "plana-working-building.apng": {"x": -6, "y": 0},
                "plana-working-juggling.apng": {"x": -6, "y": 0},
                "plana-working-conducting.apng": {"x": -6, "y": 0},
                "plana-working-sweeping.apng": {"x": -10, "y": 0},
                "plana-working-carrying.apng": {"x": -10, "y": 0},
                "plana-mini-idle.apng": {"x": 0, "y": 58},
                "plana-mini-alert.apng": {"x": 0, "y": 58},
                "plana-mini-happy.apng": {"x": 0, "y": 58},
                "plana-mini-enter.apng": {"x": 0, "y": 58},
                "plana-mini-peek.apng": {"x": 0, "y": 58},
                "plana-mini-typing.apng": {"x": 0, "y": 58},
                "plana-mini-crabwalk.apng": {"x": 0, "y": 58},
                "plana-mini-enter-sleep.apng": {"x": 0, "y": 58},
                "plana-mini-sleep.apng": {"x": 0, "y": 58},
            },
        },
    }


def referenced_files(value) -> set[str]:
    found = set()
    if isinstance(value, str) and value.endswith((".apng", ".svg", ".gif", ".png", ".webp", ".jpg", ".jpeg")):
        found.add(value)
    elif isinstance(value, list):
        for item in value:
            found |= referenced_files(item)
    elif isinstance(value, dict):
        for item in value.values():
            found |= referenced_files(item)
    return found


def validate(theme: dict[str, object], expected: dict[str, dict[str, object]]) -> dict[str, object]:
    referenced = referenced_files(theme)
    missing = sorted(name for name in referenced if not (ASSETS / name).exists())
    assets = {}
    for path in sorted(ASSETS.glob("*.apng")):
        im = Image.open(path)
        frame_count = getattr(im, "n_frames", 1)
        durations = []
        for idx in range(frame_count):
            im.seek(idx)
            durations.append(im.info.get("duration"))
        assets[path.name] = {
            "size": list(im.size),
            "frames": frame_count,
            "durationMsValues": sorted({float(d) for d in durations if d is not None}),
            "expectedFrames": expected.get(path.name, {}).get("frames"),
        }
    frame_mismatches = sorted(
        name
        for name, value in assets.items()
        if value["expectedFrames"] is not None and value["frames"] != value["expectedFrames"]
    )
    duration_mismatches = sorted(
        name
        for name, value in assets.items()
        if value["durationMsValues"] != [float(FRAME_MS)]
    )
    return {
        "ok": not missing
        and not frame_mismatches
        and not duration_mismatches
        and all(v["size"] == list(CANVAS) for v in assets.values()),
        "missingReferencedFiles": missing,
        "frameMismatches": frame_mismatches,
        "durationMismatches": duration_mismatches,
        "assetCount": len(assets),
        "referencedAssetCount": len(referenced),
        "assets": assets,
    }


def contact_sheet(previews: dict[str, list[Image.Image]]) -> Path:
    asset_names = sorted(previews)
    cols = 6
    thumb = (88, 66)
    label_h = 18
    row_h = thumb[1] + label_h + 8
    sheet = Image.new("RGBA", (cols * thumb[0] + 220, len(asset_names) * row_h + 12), (250, 252, 255, 255))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for row_idx, name in enumerate(asset_names):
        y = 8 + row_idx * row_h
        draw.text((8, y + 24), name, fill=(30, 36, 48, 255), font=font)
        sequence = previews[name]
        n = len(sequence)
        picks = [round(i * (n - 1) / (cols - 1)) for i in range(cols)]
        for col, frame_idx in enumerate(picks):
            frame = sequence[frame_idx].copy()
            frame.thumbnail(thumb, Image.Resampling.LANCZOS)
            tile = Image.new("RGBA", thumb, (238, 242, 248, 255))
            tile.alpha_composite(frame, ((thumb[0] - frame.width) // 2, (thumb[1] - frame.height) // 2))
            x = 210 + col * thumb[0]
            sheet.alpha_composite(tile, (x, y))
            draw.rectangle((x, y, x + thumb[0] - 1, y + thumb[1] - 1), outline=(210, 216, 226, 255))
            draw.text((x + 4, y + thumb[1] + 1), f"{frame_idx + 1}/{n}", fill=(70, 78, 92, 255), font=font)

    path = QA / "contact-sheet.png"
    sheet.convert("RGB").save(path)
    return path


def write_support_files(
    report: dict[str, dict[str, object]],
    previews: dict[str, list[Image.Image]],
    theme: dict[str, object],
) -> dict[str, object]:
    (OUT / "theme.json").write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(SOURCE, OUT / "source-spritesheet.webp")
    if SOURCE_JSON.exists():
        shutil.copy2(SOURCE_JSON, OUT / "source-pet.json")
    validation = validate(theme, report)
    (QA / "asset-report.json").write_text(json.dumps({"generated": report, "validation": validation}, indent=2), encoding="utf-8")
    contact_sheet(previews)
    return validation


def main() -> None:
    ensure_dirs()
    rows = extract_rows()
    report, previews = create_assets(rows)
    theme = theme_json()
    validation = write_support_files(report, previews, theme)
    print(
        json.dumps(
            {
                "out": str(OUT),
                "assets": len(report),
                "fps": round(1000 / FRAME_MS, 2),
                "validationOk": validation["ok"],
                "missing": validation["missingReferencedFiles"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
