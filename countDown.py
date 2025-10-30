# countDown.py
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from config import FONT_PATH
from image_edit import center_preview_on_screen

def draw_countdown_overlay(frame, countdown, countdown_elapsed):
    disp = center_preview_on_screen(frame)
    if countdown > 0:
        img_pil = Image.fromarray(disp)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype(FONT_PATH, 200)
        text = str(countdown)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (disp.shape[1] - text_w) // 2
        y = (disp.shape[0] - text_h) // 2 - 400
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        disp = np.array(img_pil)
    return disp
