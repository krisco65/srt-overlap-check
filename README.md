# SRT overlap check

A small, free, read-only command-line scanner for **adjacent cue overlaps in numbered UTF-8 SRT files**. It prints cue IDs and the overlap in milliseconds as JSON. It does not print subtitle dialogue or filenames, upload files, repair timings, or overwrite originals.

Python 3.9 or later; standard library only. No package installation, account or network connection required. This repository's scanner, documentation and original example are MIT-licensed.

**Help:** [Troubleshoot overlapping timestamps](OVERLAP-TROUBLESHOOTING.md) · [Release notes](RELEASE-NOTES.md) · [Input limits](#scope-and-limits)

The troubleshooting guide includes a before/after 1ms example, a free manual workflow and explanations of common rejection codes.

## Run it

Download the source repository or the free scanner release ZIP, extract it, open a terminal in its folder, and run:

```sh
python3 -B srt_overlap_check.py example.srt
```

On Windows, use `py -3 -B` if `python3` is not available. Scan more than one explicit local file by listing each path:

```sh
python3 -B srt_overlap_check.py -- "episode-01.srt" "episode-02.srt"
```

`--` lets filenames beginning with `-` be treated as paths. Paths with spaces need quotes. Output identifies inputs by their 1-based argument order, so your filenames are not copied into the report. The scanner does not traverse directories or expand patterns itself; your shell may expand an unquoted wildcard before running it. Use explicit paths when you want a precise input list.

## A 1ms overlap, exactly

The included `example.srt` has:

```srt
1
00:00:01,000 --> 00:00:02,001
Example A

2
00:00:02,000 --> 00:00:03,000
Example B
```

Cue 1 ends at 2,001ms; cue 2 starts at 2,000ms. The result is:

```json
{
  "scope": "adjacent_cues",
  "files": [
    {
      "input": 1,
      "status": "scanned",
      "cue_count": 2,
      "overlaps": [
        {"cue_id": "1", "next_cue_id": "2", "overlap_ms": 1}
      ]
    }
  ]
}
```

A positive `overlap_ms` means the earlier cue ends after the next begins. Exactly touching boundaries produce no finding. Same-start and larger overlaps are reported too. An overlap can be intentional, such as simultaneous dialogue; a finding is not an instruction to remove it.

Exit codes: **0** = every file scanned and no adjacent overlaps; **1** = at least one overlap, no rejected files; **2** = at least one file rejected or invalid command usage. A rejected file does not stop other inputs from being scanned. If any file is rejected, do not interpret the overall scan as clean.

## Scope and limits

- At most 50 files per invocation, 2 MiB per file and 10,000 cues per file. Files are processed one at a time.
- UTF-8 with or without BOM; LF, CRLF or CR line endings. Decimal cue IDs up to 128 digits. Timing lines use comma milliseconds and 2–4 hour digits, such as `00:00:01,000 --> 00:00:02,000`.
- Rejects invalid UTF-8, NUL bytes, missing cue text, malformed timing lines, duplicate numeric IDs (`1` and `001` count as duplicates), nonpositive durations and starts that move backward.
- Position extensions, unnumbered subtitles and other SRT dialects are unsupported. Same-start cues are accepted and overlapping adjacent cues are reported.
- Checks neighboring cues in file order, not every intersecting pair. For a long cue spanning several later cues, this is not an exhaustive pair list. It does not analyze audio, synchronization, reading speed, translation quality or platform compliance.
- Reads regular local files only. Directories and special files are refused; symlinks are refused where the operating system supports `O_NOFOLLOW`. An inaccessible input yields a fixed error code, without its path or contents.

The scanner itself has no network code and opens inputs read-only. Your terminal, operating system, shell history or any tool you use to share the output has its own behavior. JSON contains numeric cue IDs, counts and timing deltas, never dialogue. Keep sensitive paths out of commands you intend to share.

## What to do with a finding

Review the timing in your subtitle editor. [Subtitle Edit](https://github.com/SubtitleEdit/subtitleedit) is a free, more comprehensive alternative with editing and batch capabilities. This small scanner is useful when you only want a local, scriptable overlap report.

For a different workflow, I also sell **[SRT Micro-Overlap Repair — $12 one-time](https://krisco65.gumroad.com/l/srt-micro-overlap-repair)**: an offline browser utility with a review screen, batch repaired copies and CSV/JSON SHA-256 receipts. It proposes only 1–4ms end-time trims; files with larger, nested or same-start overlaps stay manual-review only. It is not a general subtitle editor or a compliance guarantee. You can [view the demonstration](https://srt-micro-overlap-repair.krisco65.chatgpt.site).

The paid GUI is separate software with its own license; the MIT license here does not grant rights to redistribute that paid package. No purchase is needed to use, modify or redistribute this scanner under MIT.

## Test

Run these tests from the source repository; tests are omitted from the downloadable release ZIP.

```sh
python3 -B -m unittest discover -v
```

Six tests cover the overlap boundary, UTF-8/BOM/CRLF and literal markup, malformed input, limits, and CLI output/privacy plus unchanged input hashes. Tests create temporary synthetic files and remove them afterward. No customer subtitles or third-party fixtures are included.

### Missing cue separators (v1.0.1)

A numeric line followed by a timestamp-looking arrow line inside cue dialogue is rejected as `missing_cue_separator`. This may mean a blank line between cues is missing. Inspect and correct a copy manually; the tool does not guess where to split it. Literal dialogue that quotes this header pattern is also unsupported. Ordinary multiline dialogue remains supported.
