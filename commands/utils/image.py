from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

async def memberCardImageProcessing(ctx, image: Image, text: str) -> Image:
    draw = ImageDraw.Draw(image)
    primaryFont = ImageFont.truetype("assets/fonts/Centrale Sans/Centrale Sans Medium.otf", 46)
    secondaryFont = ImageFont.truetype("assets/fonts/Centrale Sans/Centrale Sans Regular.otf", 40)

    # primaryFont = ImageFont.truetype("assets/fonts/Squad-Regular.otf", 64)
    # secondaryFont = ImageFont.truetype("assets/fonts/Squad-Regular.otf", 46)

    buffer_avatar = BytesIO(await ctx.display_avatar.replace(format="png", size=1024, static_format="png").read())
    avatar = Image.open(buffer_avatar).convert("RGBA")
    avatar.thumbnail((225, 225), Image.ANTIALIAS)
    avatar = add_corners(avatar, 12)

    bg_w, bg_h = image.size
    offset = (20, (bg_h - 225) // 2 + 1)
    image.paste(avatar, offset, avatar)

    txt_w, _ = draw.textsize(text, font=primaryFont)

    calc_w = bg_w - (bg_w / 2) + ((bg_w / 2) / 2) - (txt_w / 2)
    calc_h = bg_h / 2 - 30


    draw.text((calc_w, calc_h), text, (255, 255, 255), font=primaryFont)

    txt_w, _ = draw.textsize(ctx.name, font=secondaryFont)

    calc_w = bg_w - (bg_w / 2) + ((bg_w / 2) / 2) - (txt_w / 2)
    calc_h = bg_h / 2 + 30

    draw.text((calc_w, calc_h), ctx.name, (255, 255, 255), font=secondaryFont)
    return image

def add_corners(image, radius):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', image.size, 255)
    w, h = image.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    image.putalpha(alpha)
    return image