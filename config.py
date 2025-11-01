# config.py
from PIL import ImageFont

# ===== 전역 설정 (원본 스크립트 기준) =====
SAVE_ROOT = "photos"

# folder to be changed in google drive
# Google API - named to be 'credentials.json'
GOOGOLE_FOLDER_ID = "1Md5eO7SuPzY1UP-8oq22rqWG58uziPAm"

# 인쇄/아트보드
PRINT_WIDTH = 384
LOGO_PATH = "logo/logo.jpg"
FONT_PATH = "/System/Library/Fonts/Supplemental/GothamBold.ttf"
MESSAGE_TEXT = "HOLYWIN"
START_TEXT = "PRESS THE BUTTON!"

UPLOAD_FILE_TYPE ="layout" # "animation" or "layout"

# photo timing control
SHOT_TIMES = [4, 8]
COUNT_SOUND_PATHS = {
    4: "sound_updated/ready.mp3",
    3: "sound_updated/3.mp3",
    2: "sound_updated/2.mp3",
    1: "sound_updated/1.mp3",
    0: "sound_updated/shot.mp3"
    }

# Layout Setting
TOP_MARGIN = 50
BOTTOM_MARGIN = 0
EXTRA_MARGIN = 20
y_offset_value = 50

# GIF Layout Setting
CANVAS_W = 400
LOGO_H = 50
TEXT_H = 50
DATE_H = 40
MARGIN = 20
max_logo_w = CANVAS_W - 2*MARGIN - 100
GIF_BOTTOM_MARGIN = 80

# 폰트 
font_S = ImageFont.truetype(FONT_PATH, 32)
font_L = ImageFont.truetype(FONT_PATH, 65)
gif_font_L = ImageFont.truetype(FONT_PATH, 65)
gif_font_S = ImageFont.truetype(FONT_PATH, 32)
START_font = ImageFont.truetype(FONT_PATH, 80)


# QR code Setting
QR_SIZE = 300


# Camera crop
CROP_LEFT = 200
CROP_RIGHT = 200
CROP_TOP = 0
CROP_BOTTOM = 0
PREVIEW_W = 1920
PREVIEW_H = 1135
BACKGROUND_COLOR = 245

# Image stillcut Setting
ALPHA_VALUE = 1.5
BETA_VALUE = 20

# GIF
TARGET_GIF_WIDTH = 480
GIF_FPS = 5
GIF_COLORS = 256
GIF_DURATION = SHOT_TIMES[-1] + 1
FRAME_INTERVAL = 1.0 / GIF_FPS
GIF_DURATION_TIME = 50 # duration per frame in milliseconds

# 화면 (미리보기 캔버스)
FALLBACK_SCREEN_W = 1920
FALLBACK_SCREEN_H = 1080

# 여백
PHOTO_MARGIN = 10

# printer setting
PRINTER_VENDOR_ID = 0x0485
PRINTER_PRODUCT_ID = 0x5741