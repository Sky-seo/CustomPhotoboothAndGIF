# camera.py
import cv2, time, os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from config import (
    SAVE_ROOT, FRAME_INTERVAL, SHOT_TIMES, GIF_DURATION,GIF_DURATION_TIME,
    TARGET_GIF_WIDTH, GIF_COLORS, FONT_PATH
)
from image_edit import crop_frame
from countDown import draw_countdown_overlay

# ===== gif record =====

def record_gif(cap):
    frames = []
    stills = []
    start = time.time()
    last_capture = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = os.path.join(SAVE_ROOT, timestamp)
    os.makedirs(save_dir, exist_ok=True)
    shot_done = [False] * len(SHOT_TIMES)
    flash_duration = 0.15
    flash_start = None

    print("🎥 촬영 시작 — crop 적용됨")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # ✅ 항상 crop 적용
        frame = crop_frame(frame)
        mirrored_frame = cv2.flip(frame, 1)
        now = time.time()
        elapsed = now - start
        if elapsed >= GIF_DURATION:
            break

        # 카운트다운 계산
        countdown = 0
        countdown_elapsed = 0
        for t in SHOT_TIMES:
            diff = t - elapsed
            if 0 <= diff <= 5:
                countdown = int(diff) + 1
                countdown_elapsed = 5 - diff
                break

        # 플래시 타이밍
        FLASH_OFFSET = 0.1
        FLASH_TOLERANCE = 0.05
        for t in SHOT_TIMES:
            trigger_time = t + FLASH_OFFSET
            if abs(elapsed - trigger_time) < FLASH_TOLERANCE and flash_start is None:
                flash_start = now

        # 디스플레이 오버레이
        disp = draw_countdown_overlay(mirrored_frame, countdown, countdown_elapsed)

        # 플래시 효과
        if flash_start is not None and (now - flash_start) < flash_duration:
            white_overlay = np.ones_like(disp, dtype=np.uint8) * 255
            disp = cv2.addWeighted(white_overlay, 1, disp, 1, 0)
        elif flash_start is not None and (now - flash_start) >= flash_duration:
            flash_start = None

        # GIF 프레임 저장
        if now - last_capture >= FRAME_INTERVAL:
            frame_rgb = cv2.cvtColor(mirrored_frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame_rgb))
            last_capture = now

        # 스틸컷 저장
        for idx, t in enumerate(SHOT_TIMES):
            if not shot_done[idx] and abs(elapsed - t) < 0.25:
                stills.append(mirrored_frame.copy())
                img_path = os.path.join(save_dir, f"photo_{idx+1}.png")
                cv2.imwrite(img_path, mirrored_frame)
                print(f"💾 컬러 스틸컷 저장: {img_path}")
                shot_done[idx] = True

        # 미리보기 표시
        cv2.imshow("PhotoBooth", disp)
        cv2.waitKey(1)

    # 🎬 촬영 종료 → PROCESSING 화면 표시
    print("🧩 PRINTING...")
    black = np.zeros((720, 1280, 3), dtype=np.uint8)
    img_pil = Image.fromarray(black)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(FONT_PATH, 120)
    text = "PRINTING..."
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(((1280 - text_w)//2, (720 - text_h)//2), text, font=font, fill=(255,255,255))
    black = np.array(img_pil)
    cv2.imshow("PhotoBooth", black)
    cv2.waitKey(1)

    # 🪄 GIF 저장
    gif_path = os.path.join(save_dir, "animation.gif")
    if frames:
        resized_frames = []
        for f in frames:
            w, h = f.size
            f = f.resize((TARGET_GIF_WIDTH, int(h * (TARGET_GIF_WIDTH / w))), Image.LANCZOS)
            f = f.convert('P', palette=Image.ADAPTIVE, colors=GIF_COLORS)
            resized_frames.append(f)
        resized_frames[0].save(
            gif_path,
            save_all=True,
            append_images=resized_frames[1:],
            duration=GIF_DURATION_TIME,
            loop=0,
            optimize=True,
            disposal=2
        )
        print(f"✅ GIF 저장 완료: {gif_path}")
    else:
        print("⚠️ GIF 프레임이 없습니다.")

    return gif_path, stills, save_dir
