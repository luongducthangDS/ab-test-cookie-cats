"""Download the Cookie Cats data (not redistributed here: its source repository states no license)."""
import hashlib
import urllib.request
from pathlib import Path

URL = ("https://raw.githubusercontent.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats/"
       "master/cookie_cats.csv")
SHA256 = "5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd"
OUT = Path(__file__).resolve().parents[1] / "data" / "cookie_cats.csv"

if not OUT.exists():
    OUT.parent.mkdir(exist_ok=True)
    urllib.request.urlretrieve(URL, OUT)
digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
if digest != SHA256:
    OUT.unlink()
    raise SystemExit(f"checksum mismatch ({digest}); the source file changed, results may not reproduce")
print(f"ok: {OUT} ({OUT.stat().st_size:,} bytes, sha256 verified)")
