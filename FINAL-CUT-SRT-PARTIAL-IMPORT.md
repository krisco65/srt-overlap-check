# Final Cut Pro SRT overlap errors and partial imports: check them separately

If Final Cut Pro imports only part of an SRT file and marks some captions red, do not assume that trimming overlaps will restore the missing captions. Check import completeness and caption timing as separate questions.

Apple's documentation distinguishes SRT overlap warnings from invalid-character warnings. It directs users to the Validation section of the Captions inspector and provides a built-in overlap command. [Apple: caption validation](https://support.apple.com/en-ca/101629).

## First, establish whether the import is complete

Keep the original SRT and work on a copy. Note where the imported captions stop, then compare that point with the remaining cues in the source. A later cue in the source is a reason to investigate missing content; it is not proof of a specific parser defect.

For a local structural check, download the [free SRT overlap scanner v1.0.1](https://github.com/krisco65/srt-overlap-check/releases/tag/v1.0.1), extract it, and run:

```sh
python3 -B srt_overlap_check.py -- "captions.srt"
```

The JSON includes `cue_count`, adjacent overlap pairs and any rejection code. It does not print dialogue or filenames. It cannot inspect Final Cut's timeline, and its cue count is not a guarantee that Final Cut accepts every cue.

| Scanner result | What it establishes | What to do next |
| --- | --- | --- |
| `missing_cue_separator` | A numeric line and timing-looking arrow occur inside cue dialogue. | Inspect the possible missing blank line; do not automatically split dialogue that may be quoting a cue header. |
| `invalid_utf8` or `invalid_timestamp` | The file is outside this scanner's accepted input syntax. | Inspect/re-export a copy in the supported format before relying on the overlap results. |
| Successful scan with overlap pairs | The parsed adjacent cues overlap by the reported amounts. | Review those intervals separately from any missing-import problem. |
| Successful scan with no pairs | No adjacent overlaps were found among the parsed cues. | If Final Cut still truncates the import, investigate its specific message and the source near the cutoff. Do not buy an overlap repair expecting it to restore missing captions. |

A successful scan is not a full SRT conformance test. The free scanner has explicit size, syntax and cue limits; read its README. Exit code 1 means overlaps found, while 2 means an error or rejected input. Neither is a successful clean scan.

Try the original synthetic fixtures: [100ms overlap](examples/large-overlap.srt), [missing separator](examples/missing-separator.srt), and [no-overlap control](examples/no-overlap.srt). Their [recorded scanner results](examples/expected-results.json) have exit codes 1, 2 and 0 respectively. These are scanner tests, not Final Cut import tests.

## Then resolve the timing issue using the editor you already have

For SRT overlap warnings, Apple documents **Edit > Captions > Resolve Overlaps**, or adjusting caption position/duration. Review the intended timing before using a bulk command, especially for simultaneous dialogue. Apple's separate guidance for SRT invalid-character warnings concerns multiple adjacent line breaks within caption text. The blank separator between SRT cue blocks has a different structural role; do not delete every blank line from the file. [Apple's SRT guidance](https://support.apple.com/en-ca/101629).

A firsthand Apple Community report describes an hour-long SRT with only an initial portion imported; its author had already tried fixing overlaps without resolving the problem. That is an example of why these symptoms should be investigated separately, not a diagnosis of your file. [Original discussion](https://discussions.apple.com/thread/254698464).

For broader independent validation, [Subtitle Edit's current command-line documentation](https://github.com/SubtitleEdit/subtitleedit/blob/main/docs/reference/command-line.md) describes `seconv lint` and bulk conversion/error-fixing workflows. Follow its installation and version-specific instructions. No third-party editor command has been run against your file by this guide.

## When a narrow repair tool is relevant

If the file parses correctly and your reviewed issue is specifically a 1–4ms end-time overlap, [SRT Micro-Overlap Repair](https://krisco65.gumroad.com/l/srt-micro-overlap-repair) offers an optional $12 offline GUI for reviewed batch copies and CSV/JSON SHA-256 receipts. Larger, nested or same-start overlaps make the entire file manual-review only. It does not repair incomplete imports, reconstruct missing captions, merge simultaneous speakers or certify Final Cut compatibility.

You can [use the free browser check](https://srt-micro-overlap-repair.krisco65.chatgpt.site) before considering the paid workflow. If Final Cut's built-in command already meets your needs, no separate purchase is necessary.
