# printer_utils.py
import os, time
from escpos.printer import Usb

printer_instance = None

def get_printer(vendor_id=0x0485, product_id=0x5741, interface=0, in_ep=0x81, out_ep=0x03):
    global printer_instance
    if printer_instance is None:
        print("🖨️ 프린터 초기화 중...")
        printer_instance = Usb(vendor_id, product_id, interface=interface, in_ep=in_ep, out_ep=out_ep, timeout=3000)
        try:
            printer_instance.charcode("USA")
        except Exception:
            pass
    return printer_instance


def print_strip(image_path):
    if not os.path.exists(image_path):
        print(f"❌ 파일을 찾을 수 없습니다: {image_path}")
        return False

    try:
        p = get_printer()
        p.image(image_path)
        p.text("\n\n")
        p.cut()
        print(f"✅ 인쇄 완료: {image_path}")
        return True

    except Exception as e:
        print(f"⚠️ 인쇄 실패: {e}")
        return False
