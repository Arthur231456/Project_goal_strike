from PIL import ImageDraw, Image

img = Image.open("health2.jpg")
image = img.transpose(Image.FLIP_LEFT_RIGHT)
image = image.resize((28, 28))
image.save("health2.jpg")