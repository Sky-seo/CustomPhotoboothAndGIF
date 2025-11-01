# photobooth.py
import os, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
from camera import record_gif
from image_edit import process_photo, build_strip, build_layout_gif, center_preview_on_screen, crop_frame
from googleDrive import upload_to_google_drive
from config import LOGO_PATH, FONT_PATH, START_TEXT, START_font, UPLOAD_FILE_TYPE
from printer import print_strip
import pygame
from sound import play_sound
from config import COUNT_SOUND_PATHS
pygame.mixer.init()

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 카메라를 열 수 없습니다.")
        return

    cv2.namedWindow("PhotoBooth", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("PhotoBooth", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.waitKey(100)

    print("📷 대기 상태 — crop 적용된 미리보기")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # ✅ 항상 crop 적용 (대기 + 촬영 동일)
        frame = crop_frame(frame)
        display = cv2.flip(frame, 1)
        display_centered = center_preview_on_screen(display)

        # "PRESS THE BUTTON!" 텍스트 표시
        img_pil = Image.fromarray(display_centered)
        draw = ImageDraw.Draw(img_pil)
        font = START_font
        text = START_TEXT
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (display_centered.shape[1] - text_w) // 2
        y = 100
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        display_centered = np.array(img_pil)

        cv2.imshow("PhotoBooth", display_centered)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            #"ready" sound play
            print("🔊 준비 사운드 재생")
            play_sound(COUNT_SOUND_PATHS[4])

            # 촬영 시에도 crop 적용된 상태로 유지됨
            gif_path, stills, save_dir = record_gif(cap)
            photos = [process_photo(f) for f in stills]

            # -----------------------------
            # 🎞️ GIF layout
            layout_output = os.path.join(save_dir, "layout.gif")
            build_layout_gif(gif_path, LOGO_PATH, layout_output)

            # -----------------------------
            # select upload target
            if UPLOAD_FILE_TYPE == "animation":
                upload_target = gif_path
            else:
                upload_target = layout_output

            # -----------------------------
            # ☁️ Google Drive
            try:
                gif_url = upload_to_google_drive(upload_target)
                print(f"✅ Google Drive 업로드 완료 ({UPLOAD_FILE_TYPE}): {gif_url}")
            except Exception as e:
                print(f"⚠️ 업로드 실패: {e}")
                gif_url = upload_target  # failback to local file

            # -----------------------------
            # Add QR to strip
            strip = build_strip(photos, gif_url)
            strip_path = os.path.join(save_dir, "strip.png")
            strip.save(strip_path)
            print(f"🖼️ 스트립 최종 저장 완료 + QR 삽입: {strip_path}")

            # 🖨️ 프린트 출력
            print_strip(strip_path)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
