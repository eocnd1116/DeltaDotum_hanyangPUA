from pathlib import Path
from PIL import Image

folder = Path(__file__).parent

for file in folder.glob("*.png"):
    image = Image.open(file).convert("RGBA")
    shifted = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shifted.paste(image, (1, 0))
    shifted.save(file)

    print(f"Shifted: {file.name}")
