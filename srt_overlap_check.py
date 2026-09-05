#!/usr/bin/env python3
"""Read-only adjacent-cue overlap scanner. Python 3.9+, standard library only."""
import argparse
import json
import os
import re
import stat
import sys

MAX_FILES = 50
MAX_BYTES = 2 * 1024 * 1024
MAX_CUES = 10_000
TIMING = re.compile(r"[ \t]*(\d{2,4}:[0-5]\d:[0-5]\d,\d{3})[ \t]+-->[ \t]+(\d{2,4}:[0-5]\d:[0-5]\d,\d{3})[ \t]*", re.ASCII)


class InvalidSRT(ValueError):
    """Public error codes never include input content."""


def milliseconds(value):
    h, m, s, ms = map(int, re.split(r"[:,]", value))
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def scan_bytes(data):
    if len(data) > MAX_BYTES:
        raise InvalidSRT("file_size_limit")
    try:
        text = data.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        raise InvalidSRT("invalid_utf8") from None
    if "\0" in text:
        raise InvalidSRT("nul_character")
    # Preserve source bytes by never writing them; parse LF, CRLF and CR locally.
    blocks, block = [], []
    for line in re.split(r"\r\n|\r|\n", text):
        if not line.strip(" \t"):
            if block:
                blocks.append(block)
                block = []
        else:
            block.append(line)
    if block:
        blocks.append(block)
    if not blocks:
        raise InvalidSRT("empty_file")
    if len(blocks) > MAX_CUES:
        raise InvalidSRT("cue_limit")
    cues, seen = [], set()
    for block in blocks:
        if len(block) < 3:
            raise InvalidSRT("malformed_cue")
        cue_id = block[0].strip(" \t")
        if not re.fullmatch(r"[0-9]{1,128}", cue_id):
            raise InvalidSRT("invalid_cue_id")
        canonical = cue_id.lstrip("0") or "0"
        if canonical in seen:
            raise InvalidSRT("duplicate_cue_id")
        seen.add(canonical)
        match = TIMING.fullmatch(block[1])
        if not match:
            raise InvalidSRT("invalid_timestamp")
        start, end = map(milliseconds, match.groups())
        if end <= start:
            raise InvalidSRT("nonpositive_duration")
        if cues and start < cues[-1][1]:
            raise InvalidSRT("out_of_order")
        cues.append((cue_id, start, end))
    overlaps = []
    for earlier, later in zip(cues, cues[1:]):
        delta = earlier[2] - later[1]
        if delta > 0:
            overlaps.append({"cue_id": earlier[0], "next_cue_id": later[0], "overlap_ms": delta})
    return {"cue_count": len(cues), "overlaps": overlaps}


def read_local(path):
    # Nonblocking open plus fstat rejects directories/devices/FIFOs without reading them.
    # NOFOLLOW, where supported, also refuses symlinks. Nothing is created or modified.
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise InvalidSRT("not_regular_file")
        if info.st_size > MAX_BYTES:
            raise InvalidSRT("file_size_limit")
        return stream.read(MAX_BYTES + 1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read explicit local SRT paths; emit JSON without cue text or filenames. Never repairs or writes files.")
    parser.add_argument("paths", nargs="+", help="Local files, in output order; use -- before paths beginning with '-'.")
    args = parser.parse_args(argv)
    if len(args.paths) > MAX_FILES:
        print(json.dumps({"error": "file_count_limit", "max_files": MAX_FILES}))
        return 2
    reports = []
    for index, path in enumerate(args.paths, 1):
        try:
            report = {"input": index, "status": "scanned", **scan_bytes(read_local(path))}
        except InvalidSRT as exc:
            report = {"input": index, "status": "rejected", "error": str(exc)}
        except (OSError, ValueError):
            report = {"input": index, "status": "rejected", "error": "file_unreadable"}
        reports.append(report)
    print(json.dumps({"scope": "adjacent_cues", "files": reports}, indent=2))
    return 2 if any(r["status"] == "rejected" for r in reports) else 1 if any(r["overlaps"] for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main())
