from PIL import Image, ImageFont, ImageDraw
import os

from app import line_breaks
from line_breaker import format_blocks


def save_zip(blocks, font_size, filename):
    W,H = 1920, 1080
    from zipfile import ZipFile
    with ZipFile("result.zip", "w") as zipObj:
        for counter, block in enumerate(blocks,1):
            text = "\n".join(block)
            print(text)
            img = Image.open(filename)
            font = ImageFont.truetype("NotoSans-Bold.ttf", font_size)
            editable = ImageDraw.Draw(img)
            w, h = editable.textsize(text, font=font)
            editable.text(((W-w)/2, (H-h)/2), text, (255,255,255), font=font)
            img.save(f"{counter}.png")
            zipObj.write(f"{counter}.png")
            os.remove(f"{counter}.png")
    

def save_single(text, font_size, filename):
    img = Image.open(filename)
    font = ImageFont.truetype("NotoSans-Bold.ttf", font_size)
    editable = ImageDraw.Draw(img)
    editable.text((58,300), text, (255,255,255), font=font)
    img.save("result.png")


def create_image(blocks, font_size, transparent=False, single_block=False):
    if transparent:
        filename = "transparent.png"
    else:
        filename = "black.png"

    if single_block:
        filename = "big_" + filename
        filename = os.path.join("images", filename)
        paragraph = format_blocks(blocks)
        save_single(paragraph, font_size, filename)
    else:
        filename = os.path.join("images", filename)
        save_zip(blocks, font_size, filename)

