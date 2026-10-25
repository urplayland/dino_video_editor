#!/usr/bin/env python3
"""Generate five original lightweight cartoon sound effects locally (no API)."""
import math
from pathlib import Path
import random
import struct
import wave

ROOT = Path(__file__).resolve().parent
RATE = 24000


def wav(name, values):
    dest = ROOT / "output" / "sfx"
    dest.mkdir(parents=True, exist_ok=True)
    with wave.open(str(dest / f"{name}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", max(-32768, min(32767, int(v * 16000)))) for v in values))
    print(dest / f"{name}.wav")


def make(name, seconds, sound):
    rng = random.Random(42)
    samples = []
    total = int(RATE * seconds)
    for n in range(total):
        t = n / RATE
        p = n / total
        fade = min(1., p * 30, (1. - p) * 30)
        noise = rng.uniform(-1, 1)
        if sound == "whoosh":
            envelope = math.sin(math.pi * p) ** 1.8
            v = .35 * noise * envelope + .1 * math.sin(2 * math.pi * (110 + 210 * p) * t) * envelope
        elif sound == "chime":
            v = sum(.25 / (i + 1) * math.sin(2 * math.pi * f * t) for i, f in enumerate((660, 990, 1320))) * math.exp(-3.5 * t)
        elif sound == "pop":
            v = (.55 * noise + .4 * math.sin(2 * math.pi * (480 - 330 * p) * t)) * math.exp(-18 * t)
        elif sound == "footsteps":
            beat = (t * 3) % 1
            v = (noise * .35 + math.sin(2 * math.pi * 85 * t) * .25) * math.exp(-22 * beat)
        else:  # rumble
            v = (.17 * math.sin(2 * math.pi * 55 * t) + noise * .045) * math.sin(math.pi * p)
        samples.append(v * fade)
    wav(name, samples)


if __name__ == "__main__":
    for name, duration in (("whoosh", 1.2), ("chime", 2.4), ("pop", .35), ("footsteps", 2.0), ("rumble", 2.5)):
        make(name, duration, name)
