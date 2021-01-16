from PIL import ImageDraw, Image

img = Image.open("image02.png")
image = img.transpose(Image.FLIP_LEFT_RIGHT)
image = image.resize((29, 29))
image.save("image22.png")