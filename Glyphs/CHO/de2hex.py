from pathlib import Path

start = 0xA960

files = sorted(
    Path(".").glob("*.png"),
    key=lambda x: int(x.stem)
)

for i, file in enumerate(files):
    new_name = f"U+{start + i:X}.png"
    file.rename(file.with_name(new_name))
