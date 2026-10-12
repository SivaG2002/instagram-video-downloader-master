import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import download_instagram_video


class FakeYDL:
    def __init__(self, options=None):
        self.options = options or {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def extract_info(self, url, download=False):
        return {
            "formats": [
                {
                    "format_id": "video-only",
                    "vcodec": "avc1",
                    "acodec": None,
                    "height": 720,
                    "tbr": 2000,
                },
                {
                    "format_id": "audio-only",
                    "vcodec": None,
                    "acodec": "mp4a",
                    "tbr": 128,
                },
                {
                    "format_id": "combined",
                    "vcodec": "avc1",
                    "acodec": "mp4a",
                    "height": 1080,
                    "tbr": 4000,
                },
            ]
        }

    def download(self, urls):
        return None


class DownloadInstagramVideoTests(unittest.TestCase):
    def test_missing_gstreamer_does_not_emit_fallback_message(self):
        with patch.object(download_instagram_video, "yt_dlp", type("Dummy", (), {"YoutubeDL": FakeYDL})()), \
             patch.object(download_instagram_video.shutil, "which", return_value=None), \
             patch.object(download_instagram_video, "fetch_instagram_media", side_effect=AssertionError("should not use fallback fetch")):
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_path = Path(temp_dir) / "result.mp4"
                    result = download_instagram_video.download_instagram_post(
                        "https://www.instagram.com/p/test/",
                        output_path,
                    )

            self.assertEqual(result, output_path)
            self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
