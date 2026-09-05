# Troubleshooting overlapping SRT timestamps

An overlap means one cue ends after the next cue starts. First establish whether the overlap is intentional. The number alone cannot tell you: even a 1–4ms overlap can be deliberate, and a larger one can be a mistake.

## Find the boundary without changing your subtitles

From the scanner folder, run:

```sh
python3 -B srt_overlap_check.py -- "episode.srt"
```

The scanner reads your local file and prints JSON. For example:

```json
{"cue_id": "1", "next_cue_id": "2", "overlap_ms": 1}
```

This identifies a 1ms overlap from cue 1 into cue 2. The report contains no dialogue or filenames. For multiple inputs, `input: 1` means the first path you supplied. Exit code 1 means overlaps were found; it is not a crash. Exit code 2 means something was rejected, so check the per-file `error` before drawing conclusions.

Try the included synthetic example first:

```sh
python3 -B srt_overlap_check.py example.srt
```

## Decide whether an edit is appropriate

| Finding | What to check |
| --- | --- |
| Earlier end is 1–4ms after the next start | Review the nearby dialogue and intended boundary. A tiny discrepancy is a candidate for a small trim, not proof of an error. |
| Both cues start at the same time | Check whether simultaneous dialogue or intentionally concurrent captions are involved. Do not resolve this automatically. |
| One cue extends beyond the end of the next cue | Inspect the full interval. Trimming this nested overlap may remove intended display time. |
| Overlap is larger than 4ms | Review in a subtitle editor with the media. A narrow boundary-trim tool is not a general timing repair. |

The scanner reports adjacent pairs only. A long cue spanning several later cues may have additional intersections that are not listed. A report without findings does not certify audio synchronization, reading speed or delivery-platform compliance.

## Exact before and after for a reviewed 1ms trim

Suppose you have reviewed the scene and determined that cue 1 should end when cue 2 starts. The original timing is:

```srt
1
00:00:01,000 --> 00:00:02,001
Example A

2
00:00:02,000 --> 00:00:03,000
Example B
```

A 1ms end-time trim changes **only cue 1's end** from `00:00:02,001` to `00:00:02,000`:

```srt
1
00:00:01,000 --> 00:00:02,000
Example A

2
00:00:02,000 --> 00:00:03,000
Example B
```

Cue starts and dialogue stay unchanged. The two boundaries now touch; this scanner reports no overlap for that pair. This example does not prescribe a minimum gap required by a particular delivery specification.

## Free manual workflow

1. Keep the original and work on a copy in your subtitle editor or a plain-text editor that preserves UTF-8.
2. Find the reported cue IDs and review the interval with the media. If concurrent display is intended, leave it intact.
3. For a confirmed tiny boundary error, change only the earlier end timestamp to the next start. Ensure the earlier cue still ends after its own start.
4. Save the copy with the intended encoding and line endings, then scan that copy. Review the change in your playback or delivery workflow as well.

[Subtitle Edit](https://github.com/SubtitleEdit/subtitleedit) is a free, fuller subtitle editor. This scanner neither replaces an editor nor performs any repair itself.

## If the scanner rejects a file

| Error | Next step |
| --- | --- |
| `missing_cue_separator` | Inspect a possible cue header inside dialogue. Restore a missing blank separator in a copy only after review; literal quoted cue headers are also unsupported. |
| `invalid_utf8` | Re-export a copy as UTF-8. Do not merely rename its extension. |
| `duplicate_cue_id` | Inspect duplicated numeric indices; `1` and `001` are the same ID to this scanner. |
| `invalid_timestamp` | Check comma milliseconds and `HH:MM:SS,mmm --> HH:MM:SS,mmm`. Position extensions and other dialects are unsupported. |
| `out_of_order` | Inspect cues whose starts move backward in file order. Do not blindly sort dialogue. |
| `nonpositive_duration` | Find a cue that ends at or before its start and review its intended interval. |
| `file_size_limit` / `cue_limit` | Use a tool suited to larger files; this scanner accepts 2 MiB and 10,000 cues per file. |
| `file_unreadable` / `not_regular_file` | Supply a readable regular local file, not a directory, device or unsupported symlink. |

The [README](README.md#scope-and-limits) describes all supported input limits. A rejected file is not a clean file.

## Optional batch repair with review and receipts

I also sell [SRT Micro-Overlap Repair for $12 one-time](https://krisco65.gumroad.com/l/srt-micro-overlap-repair), a separate offline browser tool. It proposes reviewed 1–4ms end-time trims, downloads repaired copies, and includes CSV/JSON SHA-256 receipts. Files with same-start, nested or larger overlaps remain manual-review only, with no repairs applied to that file. It is not an audio-sync or compliance tool.

[View the demonstration](https://srt-micro-overlap-repair.krisco65.chatgpt.site) to see the workflow. The free scanner and manual workflow remain available without a purchase. The paid tool has a separate license.
