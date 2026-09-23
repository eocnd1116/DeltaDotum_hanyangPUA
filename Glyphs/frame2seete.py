from pathlib import Path
from PIL import Image

X = 16
Y = 16
SIZE = 13

files = sorted(Path(__file__).parent.glob("*.png"))

files = files[:X * Y]

sheet = Image.new("RGBA", (X * SIZE, Y * SIZE), (0, 0, 0, 0))

for i, file in enumerate(files):
    image = Image.open(file).convert("RGBA")

    if image.size != (SIZE, SIZE):
        raise ValueError(
            f"{file.name}: expected {SIZE}x{SIZE}, "
            f"got {image.width}x{image.height}"
        )

    x = (i % X) * SIZE
    y = (i // X) * SIZE

    sheet.alpha_composite(image, (x, y))

sheet.save("spritesheet.png")
