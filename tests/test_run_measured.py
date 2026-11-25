"""BUG-MED-001 regression: when the CLI cannot start, run_measured.py must exit with an error and stop its
lag probe (a separate process) instead of hanging forever. Windows-only, needs psutil and soundfile; does not
touch the GPU beyond an `nvidia-smi` memory query (skipped when nvidia-smi is missing)."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "run_measured.py"
TIMEOUT_S = 60


@unittest.skipUnless(sys.platform == "win32" and shutil.which("nvidia-smi"), "Windows with nvidia-smi only")
class MissingCliTest(unittest.TestCase):
    def test_BUG_MED_001_missing_cli_does_not_hang(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            proc = subprocess.run(
                [sys.executable, "-I", "-B", str(SCRIPT), "--cli", str(out / "missing.exe"), "--modelo", "m.gguf",
                 "--saida", str(out), "--rotulo", "x", "--texto", "Hi.", "--sem-base"],
                capture_output=True, text=True, timeout=TIMEOUT_S)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse((out / "x.durante.parar").exists(), "probe stop file left behind")


if __name__ == "__main__":
    unittest.main()
