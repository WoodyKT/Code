from inky.auto import auto
from PIL import Image

print("Updating Inky Impression display...")
try:
    inky_display = auto()
    img = Image.open("screenshot.png").convert("RGB")
    img = img.resize(inky_display.resolution)
    inky_display.set_image(img)
    inky_display.show()
    print("Inky display updated.")
except:
    print("Error, likely no inky screen connected")