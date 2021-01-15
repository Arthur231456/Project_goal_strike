from PIL import ImageDraw, Image

img = Image.open("health.jpg")

image = img.resize((30, 30))
image.save("health1.jpg")