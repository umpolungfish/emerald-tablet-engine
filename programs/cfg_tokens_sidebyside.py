"""
Side-by-side sync of animated_cfg_tokens.gif (2D) and
animated_cfg_tokens_top.gif (3D overhead).

Frames are zipped in lock-step; the shorter GIF loops to match the longer.
Output: docs/animated_cfg_tokens_sidebyside.gif
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
LEFT  = root / "docs" / "animated_cfg_tokens.gif"
RIGHT = root / "docs" / "animated_cfg_tokens_top.gif"
OUT   = root / "docs" / "animated_cfg_tokens_sidebyside.gif"

GAP   = 6   # px between the two panels
BG    = (13, 13, 26)


def extract_frames(path: Path) -> tuple[list[Image.Image], int]:
    gif = Image.open(path)
    frames = []
    try:
        while True:
            frames.append(gif.copy().convert("RGB"))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    duration = gif.info.get("duration", 55)
    return frames, duration


def main(speed: float = 1.0) -> None:
    print(f"Loading {LEFT.name} ...")
    lf, ld = extract_frames(LEFT)
    print(f"  {len(lf)} frames  {lf[0].size}")

    print(f"Loading {RIGHT.name} ...")
    rf, rd = extract_frames(RIGHT)
    print(f"  {len(rf)} frames  {rf[0].size}")

    n = max(len(lf), len(rf))
    duration = int(min(ld, rd) / speed)   # scale by speed factor

    # Normalise heights — scale the shorter panel to match the taller
    lh = lf[0].height
    rh = rf[0].height
    if lh != rh:
        target = max(lh, rh)
        if lh < target:
            lw = int(lf[0].width * target / lh)
            lf = [f.resize((lw, target), Image.LANCZOS) for f in lf]
        else:
            rw = int(rf[0].width * target / rh)
            rf = [f.resize((rw, target), Image.LANCZOS) for f in rf]

    H  = lf[0].height
    LW = lf[0].width
    RW = rf[0].width
    W  = LW + GAP + RW

    print(f"Compositing {n} frames ({W}×{H}) ...")
    out_frames: list[Image.Image] = []
    for i in range(n):
        l = lf[i % len(lf)]
        r = rf[i % len(rf)]
        canvas = Image.new("RGB", (W, H), BG)
        canvas.paste(l, (0, 0))
        canvas.paste(r, (LW + GAP, 0))
        out_frames.append(canvas)
        if (i + 1) % 20 == 0 or i == n - 1:
            print(f"\r  {(i+1)/n*100:5.1f}%  frame {i+1}/{n}", end="", flush=True)

    print()
    suffix = f"_slow{int(round(1/speed))}x" if speed < 1.0 else ""
    out_path = root / "docs" / f"animated_cfg_tokens_sidebyside{suffix}.gif"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving -> {out_path} ...")
    out_frames[0].save(
        str(out_path), save_all=True, append_images=out_frames[1:],
        duration=duration, loop=0, optimize=False,
    )
    sz = out_path.stat().st_size / (1024 * 1024)
    print(f"Done: {out_path}  ({sz:.1f} MB)")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--speed", type=float, default=1.0,
                    help="Playback speed multiplier (e.g. 0.25 = quarter speed)")
    args = ap.parse_args()
    main(speed=args.speed)
