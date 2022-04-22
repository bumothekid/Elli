import nextcord
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

async def welcomeImageProcessing(ctx, image: Image) -> Image:
    draw = ImageDraw.Draw(image)
    primaryFont = ImageFont.truetype("assets/fonts/Centrale Sans/Centrale Sans Regular.otf", 64)
    secondaryFont = ImageFont.truetype("assets/fonts/Centrale Sans/Centrale Sans Regular.otf", 46)

    if type(ctx) == nextcord.Interaction:
        buffer_avatar = BytesIO(await ctx.user.display_avatar.replace(format="png", size=1024, static_format="png").read())
        username = ctx.user.name
    
    if type(ctx) == nextcord.Member:
        buffer_avatar = BytesIO(await ctx.display_avatar.replace(format="png", size=1024, static_format="png").read())
        username = ctx.name

    avatar = Image.open(buffer_avatar).convert("RGBA")
    avatar.thumbnail((225, 225), Image.ANTIALIAS)
    avatar = add_corners(avatar, 12)
    # avatar = dropShadow(avatar, shadow=(0x00, 0x00, 0x00, 0xff))

    _, bg_h = image.size
    offset = (20, (bg_h - 225) // 2 + 1)
    image.paste(avatar, offset, avatar)

    draw.text((360, 80), "Willkommen!", (255, 255, 255), font=primaryFont)
    draw.text((440, 160), f"{username}", (255, 255, 255), font=secondaryFont)
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

def dropShadow(image, offset=(5,5), background=0xffffff, shadow=0x444444, border=8, iterations=3):
    totalWidth = image.size[0] + abs(offset[0]) + 2*border
    totalHeight = image.size[1] + abs(offset[1]) + 2*border

    back = Image.new(image.mode, (totalWidth, totalHeight), background)

    shadowLeft = border + max(offset[0], 0)
    shadowTop = border + max(offset[1], 0)

    back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0], shadowTop + image.size[1]])

    n = 0
    while n < iterations:
        back = back.filter(ImageFilter.BLUR)
        n += 1

    imageLeft = border - min(offset[0], 0)
    imageTop = border - min(offset[1], 0)
    back.paste(image, (imageLeft, imageTop))

    return back