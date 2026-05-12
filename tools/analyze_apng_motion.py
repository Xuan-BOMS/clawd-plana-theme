import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageSequence


def frame_metrics(frame: Image.Image) -> dict[str, float] | None:
    arr = np.array(frame.convert("RGBA"))
    alpha = arr[:, :, 3]
    ys, xs = np.where(alpha > 12)
    if xs.size == 0:
        return None
    x1, x2 = int(xs.min()), int(xs.max()) + 1
    y1, y2 = int(ys.min()), int(ys.max()) + 1
    area = int((alpha > 12).sum())
    return {
        "x": x1,
        "y": y1,
        "w": x2 - x1,
        "h": y2 - y1,
        "cx": float(xs.mean()),
        "cy": float(ys.mean()),
        "area": area,
    }


def analyze(path: Path) -> dict[str, object]:
    image = Image.open(path)
    metrics = [frame_metrics(frame) for frame in ImageSequence.Iterator(image)]
    valid = [m for m in metrics if m]
    if not valid:
        return {"file": path.name, "frames": len(metrics), "empty": True}

    widths = np.array([m["w"] for m in valid], dtype=np.float64)
    heights = np.array([m["h"] for m in valid], dtype=np.float64)
    areas = np.array([m["area"] for m in valid], dtype=np.float64)
    cxs = np.array([m["cx"] for m in valid], dtype=np.float64)
    cys = np.array([m["cy"] for m in valid], dtype=np.float64)

    def jump(values: np.ndarray) -> float:
        if values.size < 2:
            return 0.0
        return float(np.max(np.abs(np.diff(values))))

    median_area = float(np.median(areas))
    area_jump_ratio = 0.0
    if areas.size > 1 and median_area:
        area_jump_ratio = float(np.max(np.abs(np.diff(areas))) / median_area)

    width_range_ratio = float((widths.max() - widths.min()) / max(1.0, np.median(widths)))
    height_range_ratio = float((heights.max() - heights.min()) / max(1.0, np.median(heights)))

    score = (
        width_range_ratio * 100
        + height_range_ratio * 100
        + area_jump_ratio * 120
        + jump(cxs) * 1.7
        + jump(cys) * 1.7
    )

    return {
        "file": path.name,
        "frames": len(metrics),
        "wRangeRatio": round(width_range_ratio, 4),
        "hRangeRatio": round(height_range_ratio, 4),
        "areaJumpRatio": round(area_jump_ratio, 4),
        "maxCxJump": round(jump(cxs), 2),
        "maxCyJump": round(jump(cys), 2),
        "score": round(score, 2),
    }


def main() -> None:
    asset_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("themes/clawd-plana/assets")
    results = [analyze(path) for path in sorted(asset_dir.glob("*.apng"))]
    results.sort(key=lambda item: float(item.get("score", 0)), reverse=True)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
