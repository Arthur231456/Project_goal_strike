from PIL import ImageDraw, Image

img = Image.open("bullets.jpg")
image = img.resize((28, 28))
image.save("bullets.jpg")