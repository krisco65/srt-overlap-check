import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import srt_overlap_check as scanner

SAMPLE = b"1\n00:00:01,000 --> 00:00:02,001\nExample A\n\n2\n00:00:02,000 --> 00:00:03,000\nExample B\n"


class ScannerTests(unittest.TestCase):
    def test_exact_overlap_and_touching_boundary(self):
        report = scanner.scan_bytes(SAMPLE)
        self.assertEqual(report['overlaps'], [{'cue_id': '1', 'next_cue_id': '2', 'overlap_ms': 1}])
        self.assertEqual(scanner.scan_bytes(SAMPLE.replace(b'02,001', b'02,000'))['overlaps'], [])

    def test_bom_unicode_crlf_and_literal_markup(self):
        data = b'\xef\xbb\xbf' + SAMPLE.replace(b'Example A', '字幕 <script>private</script>'.encode()).replace(b'\n', b'\r\n')
        self.assertEqual(scanner.scan_bytes(data), scanner.scan_bytes(SAMPLE))
        self.assertNotIn('private', json.dumps(scanner.scan_bytes(data)))

    def test_rejects_ambiguous_or_invalid_input(self):
        cases = [(b'\xff', 'invalid_utf8'), (SAMPLE+b'\0', 'nul_character'), (SAMPLE.replace(b'\n2\n', b'\n001\n'), 'duplicate_cue_id'), (SAMPLE.replace(b'02,000', b'00,000'), 'out_of_order'), (SAMPLE.replace(b'02,001', b'01,000'), 'nonpositive_duration'), (SAMPLE.replace(b'02,001', b'02.001'), 'invalid_timestamp')]
        for data, code in cases:
            with self.subTest(code=code), self.assertRaisesRegex(scanner.InvalidSRT, '^'+code+'$'):
                scanner.scan_bytes(data)

    def test_missing_separator_and_valid_multiline(self):
        for newline in [b"\n", b"\r\n"]:
            broken = SAMPLE.replace(b"\n\n", b"\n").replace(b"\n", newline)
            with self.assertRaisesRegex(scanner.InvalidSRT, "missing_cue_separator"):
                scanner.scan_bytes(broken)
        valid = SAMPLE.replace(b"Example A", b"Line one\n123\nOrdinary dialogue\n00:00:02,000 --> 00:00:03,000")
        self.assertEqual(scanner.scan_bytes(valid), scanner.scan_bytes(SAMPLE))

    def test_limits(self):
        with self.assertRaisesRegex(scanner.InvalidSRT, 'file_size_limit'):
            scanner.scan_bytes(b'x'*(scanner.MAX_BYTES+1))
        many = '\n\n'.join(f'{i}\n00:00:00,000 --> 00:00:01,000\nx' for i in range(scanner.MAX_CUES+1)).encode()
        with self.assertRaisesRegex(scanner.InvalidSRT, 'cue_limit'):
            scanner.scan_bytes(many)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(scanner.main(['never-opened']*51), 2)
        self.assertEqual(json.loads(out.getvalue())['error'], 'file_count_limit')

    def test_cli_never_modifies_or_leaks_inputs_and_continues_after_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'private-filename.srt'
            path.write_bytes(SAMPLE)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = scanner.main([str(path), str(Path(tmp)/'missing')])
            self.assertEqual(code, 2)
            report = json.loads(out.getvalue())
            self.assertEqual(report['files'][0]['overlaps'][0]['overlap_ms'], 1)
            self.assertEqual(report['files'][1]['error'], 'file_unreadable')
            self.assertNotIn('private-filename', out.getvalue())
            self.assertNotIn('Example A', out.getvalue())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
            self.assertEqual(list(Path(tmp).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
