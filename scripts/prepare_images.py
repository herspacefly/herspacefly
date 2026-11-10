"""Prepare compact display copies; original supplied files remain untouched.

Run manually after changing assets/source raster art. Requires an existing FFmpeg.
The daily GitHub workflow uses committed display files and does not need FFmpeg.
"""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'assets/source'
display = ROOT/'assets/display'
display.mkdir(exist_ok=True)
ffmpeg = shutil.which('ffmpeg')
if not ffmpeg:
    raise SystemExit('FFmpeg is required only when preparing new display copies.')
for path in sorted(source.glob('*.webp')) + [source/'signal-seal.png']:
    scale = '128:128' if path.suffix == '.png' else '640:-2'
    args = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(path),
            '-vf', 'scale='+scale+':flags=lanczos', '-frames:v', '1', '-threads', '1']
    if path.suffix == '.webp':
        args += ['-c:v', 'libwebp', '-quality', '92', '-compression_level', '6']
    subprocess.run(args+[str(display/path.name)], check=True)
    print(path.name, path.stat().st_size, '->', (display/path.name).stat().st_size)
