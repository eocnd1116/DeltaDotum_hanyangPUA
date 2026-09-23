from pathlib import Path

folder = Path(__file__).parent

for file in folder.glob("*.png"):
    stem = file.stem

    if not stem.startswith("U+"):
        continue

    number = stem[2:]

    if len(number) != 4 or not number.isdigit():
        continue

    prefix = number[:2]
    suffix = int(number[2:])

    new_name = f"U+{prefix}{suffix:02X}.png"

    print(f"{file.name} -> {new_name}")

    file.rename(folder / new_name)
