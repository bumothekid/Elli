import nextcord
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

async def memberCardImageProcessing(ctx, image: Image, text: str) -> Image:
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

    _, bg_h = image.size
    offset = (20, (bg_h - 225) // 2 + 1)
    image.paste(avatar, offset, avatar)

    draw.text((360, 80), text, (255, 255, 255), font=primaryFont)
    draw.text((440, 160), username, (255, 255, 255), font=secondaryFont)
    return image

# def dropShadow(image: Image, offset=(0, 0), shadow=(0, 0, 0, 1), blur=5):
#     """Add a drop shadow to the image
    
#     Parameters
#     ----------
#     image : PIL.Image.Image
#         Image to add the drop shadow to
#     offset : tuple
#         Offset of the shadow
#     shadow : tuple
#         Shadow color
#     blur : int
#         Blur radius
    
#     Returns
#     -------
#     PIL.Image.Image
#         Image with drop shadow
#     """
#     if isinstance(shadow, (list, tuple)):
#         shadow = Image.new("RGBA", image.size, shadow)
#     else:
#         shadow = shadow.convert("RGBA")
#     shadow.alpha_composite(image, offset)
#     shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
#     return shadow

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