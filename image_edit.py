# image_edit.py
import os, cv2, qrcode, numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from config import (
    PRINT_WIDTH, LOGO_PATH, FONT_PATH, font_S,
    MARGIN, CROP_LEFT, CROP_RIGHT, CROP_TOP, CROP_BOTTOM,
    PREVIEW_W, PREVIEW_H, BACKGROUND_COLOR,ALPHA_VALUE, BETA_VALUE,
    MESSAGE_TEXT,font_L,QR_SIZE, TOP_MARGIN, BOTTOM_MARGIN, EXTRA_MARGIN,
    y_offset_value,CANVAS_W, LOGO_H, TEXT_H, DATE_H,MARGIN,max_logo_w,
    GIF_BOTTOM_MARGIN, gif_font_L, gif_font_S,PHOTO_MARGIN

)

# ================== 프레임 crop ================== #
def crop_frame(frame):
    h, w = frame.shape[:2]
    return frame[CROP_TOP:h - CROP_BOTTOM, CROP_LEFT:w - CROP_RIGHT]

# ================== 가운데 정렬 미리보기 ================== #
def center_preview_on_screen(frame):
    CANVAS_W = PREVIEW_W
    CANVAS_H = PREVIEW_H
    OFFSET_X = 0
    OFFSET_Y = -200
    fh, fw = frame.shape[:2]
    x_offset = (CANVAS_W - fw) // 2 + OFFSET_X
    y_offset = (CANVAS_H - fh) // 2 + OFFSET_Y
    if x_offset < 0: x_offset = 0
    if y_offset < 0: y_offset = 0
    canvas = np.ones((CANVAS_H, CANVAS_W, 3), dtype=np.uint8) * BACKGROUND_COLOR
    y_end = min(y_offset + fh, CANVAS_H)
    x_end = min(x_offset + fw, CANVAS_W)
    frame_h = y_end - y_offset
    frame_w = x_end - x_offset
    canvas[y_offset:y_end, x_offset:x_end] = frame[0:frame_h, 0:frame_w]
    return canvas

# ================== Sierra 디더링 ================== #
def sierra_dither(img):
    img = img.astype(np.float32)
    h, w = img.shape
    for y in range(h - 2):
        for x in range(2, w - 2):
            old_pixel = img[y, x]
            new_pixel = 255 if old_pixel > 127 else 0
            img[y, x] = new_pixel
            error = old_pixel - new_pixel
            img[y, x + 1] += error * 5/32
            img[y, x + 2] += error * 3/32
            img[y + 1, x - 2] += error * 2/32
            img[y + 1, x - 1] += error * 4/32
            img[y + 1, x] += error * 5/32
            img[y + 1, x + 1] += error * 4/32
            img[y + 1, x + 2] += error * 2/32
            img[y + 2, x - 1] += error * 2/32
            img[y + 2, x] += error * 3/32
            img[y + 2, x + 1] += error * 2/32
    return np.clip(img, 0, 255).astype(np.uint8)

# ================== 사진 디더링 후 회전 ================== #
def process_photo(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=ALPHA_VALUE, beta=BETA_VALUE)
    h, w = gray.shape
    scale = PRINT_WIDTH / h
    resized = cv2.resize(gray, (int(w * scale), int(h * scale)))
    dithered = sierra_dither(resized)
    pil_img = Image.fromarray(dithered)
    rotated = pil_img.rotate(-90, expand=True)
    if rotated.width != PRINT_WIDTH:
        scale_factor = PRINT_WIDTH / rotated.width
        rotated = rotated.resize((PRINT_WIDTH, int(rotated.height * scale_factor)))
    return rotated

# ================== 스트립 생성 ================== #
def build_strip(photos, qr_path):
    layout = []

    # 로고
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("L")
        max_w = int(PRINT_WIDTH * 0.7)
        if logo.width > max_w:
            logo = logo.resize((max_w, int(logo.height * (max_w / logo.width))))
        logo_canvas = Image.new("L", (PRINT_WIDTH, logo.height + 10), 255)
        logo_canvas.paste(logo, ((PRINT_WIDTH - logo.width)//2, 0))
        layout.append(logo_canvas)

    # 사진
    for i, img in enumerate(photos):
        layout.append(img)
        if i != len(photos)-1:
            layout.append(Image.new("L", (PRINT_WIDTH, PHOTO_MARGIN ), 255))

    # HOLYWIN (원본: 중앙 정렬)
    holy_img = Image.new("L", (PRINT_WIDTH, 100), 255)
    d = ImageDraw.Draw(holy_img)
    bbox = d.textbbox((0, 0), MESSAGE_TEXT, font=font_L)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    d.text(((PRINT_WIDTH - text_w)//2, (100 - text_h)//2), MESSAGE_TEXT, fill=0, font=font_L)
    layout.append(holy_img)

    # 날짜 (원본: 중앙 정렬)
    date_text = datetime.now().strftime("%Y-%m-%d")
    date_img = Image.new("L", (PRINT_WIDTH, 60), 255)
    d2 = ImageDraw.Draw(date_img)
    bbox2 = d2.textbbox((0, 0), date_text, font=font_S)
    tw = bbox2[2] - bbox2[0]
    th = bbox2[3] - bbox2[1]
    d2.text(((PRINT_WIDTH - tw)//2, (60 - th)//2), date_text, fill=0, font=font_S)
    layout.append(date_img)

    # QR
    qr = qrcode.make(qr_path).resize((QR_SIZE, QR_SIZE))
    qr_canvas = Image.new("L", (PRINT_WIDTH, 300), 255)
    qr_canvas.paste(qr, ((PRINT_WIDTH - QR_SIZE)//2, 0))
    layout.append(qr_canvas)

    # 상단/하단 여백
    total_height = sum(im.height for im in layout) + TOP_MARGIN + BOTTOM_MARGIN + EXTRA_MARGIN
    final_img = Image.new("L", (PRINT_WIDTH, total_height), 255)
    y_offset = y_offset_value
    for im in layout:
        final_img.paste(im, (0, y_offset))
        y_offset += im.height
    return final_img

# ================== layout.gif 생성 ================== #
def build_layout_gif(gif_path, logo_path, output_path):
    gif = Image.open(gif_path)
    gw, gh = gif.size
    logo = Image.open(logo_path).convert("RGBA")

    if logo.width > max_logo_w:
        ratio = max_logo_w / logo.width
        logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)))
    lw, lh = logo.size

    gif_x = (CANVAS_W - gw) // 2
    logo_x = (CANVAS_W - lw) // 2
    total_height = lh + MARGIN + gh + MARGIN + TEXT_H + DATE_H + MARGIN*2 + GIF_BOTTOM_MARGIN

    frames = []
    for frame in ImageSequence.Iterator(gif):
        base = Image.new("RGBA", (CANVAS_W, total_height), (255, 255, 255, 255))

        # 로고
        base.paste(logo, (logo_x, MARGIN), logo)
        # GIF 프레임
        f = frame.convert("RGBA")
        base.paste(f, (gif_x, MARGIN + lh + MARGIN), f)

        # HOLYWIN
        draw = ImageDraw.Draw(base)
        text = MESSAGE_TEXT
        bbox = draw.textbbox((0, 0), text, font=gif_font_L)
        text_w = bbox[2] - bbox[0]
        text_x = (CANVAS_W - text_w) // 2
        text_y = lh + MARGIN + gh + MARGIN + 30
        draw.text((text_x, text_y), text, fill=(0, 0, 0), font=gif_font_L)

        # 날짜
        date_text = datetime.now().strftime("%Y-%m-%d")
        bbox_date = draw.textbbox((0, 0), date_text, font=gif_font_S)
        date_w = bbox_date[2] - bbox_date[0]
        date_x = (CANVAS_W - date_w) // 2
        date_y = text_y + TEXT_H + 30
        draw.text((date_x, date_y), date_text, fill=(0, 0, 0), font=gif_font_S)

        frames.append(base)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=gif.info.get('duration', 100),
        disposal=2,
        optimize=False,
        quality=100
    )
    print(f"✅ layout.gif 저장 완료: {output_path}")
    return output_path
