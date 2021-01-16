from PIL import ImageDraw, Image

img = Image.open("free_place.jpg")
image = img.resize((28, 28))
image.save("free_place.jpg")