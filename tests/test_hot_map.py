"""Tests for scripts/hot_map.py (stdlib only): tier assignment per layer and printed coverage."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "hot_map.py"

USAGE = """group;expert;requests;misses
0;5;50;1
0;7;30;1
0;9;15;1
0;2;5;1
1;1;80;1
1;3;20;1
"""


class HotMapTest(unittest.TestCase):
    def test_tiers_and_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            usage, hotmap = Path(tmp) / "usage.csv", Path(tmp) / "hotmap.csv"
            usage.write_text(USAGE, encoding="utf-8")
            out = subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), str(usage), str(hotmap), "1", "1"],
                                 capture_output=True, text=True, check=True).stdout
            lines = hotmap.read_text(encoding="utf-8").splitlines()[1:]
        self.assertEqual(lines, ["0;5;vram", "0;7;ram", "1;1;vram", "1;3;ram"])
        # 200 requests: VRAM gets 50 + 80, RAM gets 30 + 20, SSD the remaining 20.
        self.assertIn("pedidos=200", out)
        self.assertIn("cobertura_vram=65.0%", out)
        self.assertIn("cobertura_ram=25.0%", out)
        self.assertIn("resto_ssd=10.0%", out)


if __name__ == "__main__":
    unittest.main()
