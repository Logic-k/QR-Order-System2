import qrcode
import os

import urllib.parse

# 생성할 QR 코드들의 기본 URL (실제 호스팅되는 사이트의 주소로 변경하세요)
BASE_URL = "https://qr-order-system2.onrender.com"

# QR 코드를 저장할 폴더 생성
output_dir = "qrcodes_floor2"
os.makedirs(output_dir, exist_ok=True)

# 2층 좌석 (1 ~ 12)
seats = range(1, 13)

for seat in seats:
    seat_name = f"2층 {seat}"
    encoded_seat = urllib.parse.quote(seat_name)
    url = f"{BASE_URL}/order?seat={encoded_seat}"
    
    # QR 코드 생성
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # 이미지 저장
    filename = os.path.join(output_dir, f"seat_2F_{seat}.png")
    img.save(filename)
    print(f"QR 코드 생성 완료: {filename} ({url})")

print("모든 2층 QR 코드가 생성되었습니다.")
