from inky.auto import auto
from PIL import Image
import sys

if sys.argv ==2:
    print("Updating Inky Impression display...")
    print(f"Image: {sys.argv[1]}")
    try:
        inky_display = auto()
        img = Image.open(sys.argv[1]).convert("RGB")
        img = img.resize(inky_display.resolution)
        inky_display.set_image(img)
        inky_display.show()
        print("Inky display updated.")
    except:
        print("Error, likely no inky screen connected")