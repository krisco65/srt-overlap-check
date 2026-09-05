# Free scanner v1.0.1

Fix: a numeric cue ID followed by a timestamp-looking arrow inside dialogue now fails closed with `missing_cue_separator`, instead of potentially reporting a malformed two-cue file as clean. Ordinary multiline dialogue remains supported. Literal dialogue quoting such a header is conservatively rejected. No repair behavior was added.

# Free scanner v1.0.0

A small read-only Python utility for checking adjacent-cue overlaps in explicit local UTF-8 SRT files. Requires Python 3.9 or later; no third-party packages or network access.

The downloadable ZIP includes the scanner, an original two-cue example, usage instructions, an overlap troubleshooting guide and the MIT license. It does not include the separate paid GUI, tests or customer files.

- Reports cue IDs and positive overlap milliseconds as JSON, without dialogue or filenames.
- Reads inputs only; does not repair, upload or overwrite them.
- Accepts at most 50 files per invocation, 2 MiB and 10,000 cues per file.
- Rejects unsupported/malformed inputs instead of treating them as clean.
- Exit codes: 0 clean scan, 1 overlaps found, 2 input or usage error.

Unzip, open a terminal in the extracted folder, then run:

```sh
python3 -B srt_overlap_check.py example.srt
```

Expected: cue 1 overlaps cue 2 by 1ms; exit code 1. This is a successful detection. See README.md for multiple files and OVERLAP-TROUBLESHOOTING.md for a reviewed manual workflow.

Limits: this is not an exhaustive list of all overlapping pairs, an editor, an audio-sync checker or a delivery-compliance validator. Small overlaps may be intentional. Tests are available in the source repository; they are omitted from the download package.
