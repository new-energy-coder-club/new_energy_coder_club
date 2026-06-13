#!/usr/bin/env python3
"""
NEC Quickstart Demo (no hardware required)

What it does:
- Simulates a differential-drive robot following a square-like trajectory.
- Logs trajectory to CSV.
- Prints a small ASCII plot so beginners can "see" it worked.

Requirements:
- Python 3.8+ (standard library only)

Usage:
    python demos/nec_quickstart/hello_nec.py --seconds 20
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class State:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0  # rad


def wrap_angle(rad: float) -> float:
    return (rad + math.pi) % (2 * math.pi) - math.pi


def step_unicycle(state: State, v: float, w: float, dt: float) -> None:
    state.x += v * math.cos(state.theta) * dt
    state.y += v * math.sin(state.theta) * dt
    state.theta = wrap_angle(state.theta + w * dt)


def controller_square(t: float) -> Tuple[float, float]:
    v = 0.40
    forward_time = 2.5
    turn_time = 1.2
    w_turn = (math.pi / 2) / turn_time
    phase = forward_time + turn_time
    t_in_phase = t % phase
    if t_in_phase < forward_time:
        return v, 0.0
    return 0.0, w_turn


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def ascii_plot(points: List[Tuple[float, float]], width: int = 60, height: int = 20) -> str:
    if not points:
        return "(no points)"
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-9)
    span_y = max(max_y - min_y, 1e-9)
    grid = [[" " for _ in range(width)] for _ in range(height)]
    def to_grid(x: float, y: float) -> Tuple[int, int]:
        gx = int((x - min_x) / span_x * (width - 1))
        gy = int((y - min_y) / span_y * (height - 1))
        return gx, (height - 1 - gy)
    for (x, y) in points:
        gx, gy = to_grid(x, y)
        grid[gy][gx] = "·"
    sx, sy = to_grid(points[0][0], points[0][1])
    ex, ey = to_grid(points[-1][0], points[-1][1])
    grid[sy][sx] = "S"
    grid[ey][ex] = "E"
    lines = ["".join(row) for row in grid]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="NEC quickstart demo (no hardware).")
    parser.add_argument("--seconds", type=float, default=20.0, help="Simulation time in seconds.")
    parser.add_argument("--dt", type=float, default=0.02, help="Time step in seconds.")
    parser.add_argument(
        "--out",
        type=str,
        default="demos/nec_quickstart/out",
        help="Output directory for logs.",
    )
    args = parser.parse_args()
    if args.seconds <= 0:
        raise SystemExit("--seconds must be > 0")
    if args.dt <= 0:
        raise SystemExit("--dt must be > 0")
    ensure_dir(args.out)
    csv_path = os.path.join(args.out, "run_log.csv")
    state = State()
    t = 0.0
    rows: List[Tuple[float, float, float, float, float, float]] = []
    points: List[Tuple[float, float]] = []
    steps = int(args.seconds / args.dt)
    for i in range(steps + 1):
        v, w = controller_square(t)
        points.append((state.x, state.y))
        rows.append((t, state.x, state.y, state.theta, v, w))
        step_unicycle(state, v, w, args.dt)
        t += args.dt
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["t", "x", "y", "theta", "v_cmd", "w_cmd"])
        writer.writerows(rows)
    dist = 0.0
    for (x0, y0), (x1, y1) in zip(points[:-1], points[1:]):
        dist += math.hypot(x1 - x0, y1 - y0)
    print("=== NEC Quickstart Demo ===")
    print(f"Sim time      : {args.seconds:.2f} s")
    print(f"Time step     : {args.dt:.3f} s")
    print(f"Steps         : {steps}")
    print(f"Distance (sim): {dist:.2f} m")
    print(f"Final pose    : x={state.x:.2f}, y={state.y:.2f}, theta={state.theta:.2f} rad")
    print(f"Log saved     : {csv_path}")
    print()
    print("Trajectory (ASCII):")
    print(ascii_plot(points))
    print()
    print("Next step: submit a PR!  -> docs/start-here/60min.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
