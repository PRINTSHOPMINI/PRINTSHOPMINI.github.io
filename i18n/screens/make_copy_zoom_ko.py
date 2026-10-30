# 복사 꿀팁 그림(images/copy/copy-zoom-density.png) 만들기 — 2026-10-30
#  - 오른쪽(축소/확대 · 농도조절)은 2017 설명서 화면(video/manual_2017/m16) 그대로 — 지금 기계와 같음
#  - 왼쪽은 지금 기계 화면대로 고침: [기본 복사][신분증 복사] 탭, 색상 설정 [컬러][흑백], 아래 신분증 복사 칸 없음
#    (근거: 매장에서 찍은 실제 화면 D:\클로드\복합기화면사진\정리\en·zh\2복사_2_축소확대_농도)
#  - 만든 뒤 영어·중국어: python -I i18n/screens/make_screens.py images/copy/copy-zoom-density.png
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'video', 'manual_2017', 'm16_복사_축소확대_농도.png')
OUT = os.path.join(ROOT, 'images', 'copy', 'copy-zoom-density.png')
F = r'C:\Windows\Fonts\malgun.ttf'
BLUE, WHITE = (30, 136, 229), (255, 255, 255)

src = Image.open(SRC).convert('RGB')
im = src.copy()
d = ImageDraw.Draw(im)
W = 383                                   # 왼쪽 칸 너비 (383에 세로 줄)
d.rectangle((0, 132, W - 1, 563), fill=WHITE)
im.paste(src.crop((0, 132, W, 454)), (0, 172))   # 0001 ~ B5 를 탭 높이(40)만큼 아래로

# 탭
d.rectangle((0, 132, 218, 169), fill=BLUE)
d.rectangle((219, 132, W - 1, 169), fill=(214, 220, 228))
d.rectangle((0, 170, W - 1, 171), fill=BLUE)
f = ImageFont.truetype(F, 17)
d.text((109, 151), '기본 복사', font=f, fill=WHITE, anchor='mm')
d.text((301, 151), '신분증 복사', font=f, fill=(70, 74, 80), anchor='mm')

# 색상 설정: 왼쪽 [컬러](흰 버튼) · 오른쪽 [흑백](선택된 파란 버튼)
y0, y1 = 236 + 40, 277 + 40
mono = im.crop((23, y0, 189, y1))
white_btn = im.crop((23, 319 + 40, 189, 360 + 40))          # A3 버튼 모양을 빌려 글자만 지움
wb = ImageDraw.Draw(white_btn)
wb.rectangle((2, 2, 163, 38), fill=(246, 246, 246))
im.paste(white_btn, (23, y0))
im.paste(mono, (194, y0))
ic = np.zeros((24, 18, 3), np.uint8)                        # 컬러 아이콘(여러 색 네모)
for yy in range(24):
    for xx in range(18):
        t = xx / 17
        top = np.array([230, 60, 60]) * (1 - t) + np.array([60, 170, 80]) * t
        bot = np.array([250, 200, 40]) * (1 - t) + np.array([50, 110, 220]) * t
        ic[yy, xx] = top * (1 - yy / 23) + bot * (yy / 23)
icon = Image.fromarray(ic)
d.rectangle((32, y0 + 7, 51, y0 + 32), fill=(200, 200, 200))
im.paste(icon, (33, y0 + 8))
d.text((120, (y0 + y1) // 2), '컬러', font=ImageFont.truetype(F, 18), fill=(40, 40, 40), anchor='mm')

out = im.crop((0, 30, 765, 565)).resize((1148, 802), Image.LANCZOS)
o = ImageDraw.Draw(out)
for x0, yy0, x1, yy1 in [(403, 278, 746, 440), (403, 454, 746, 518)]:
    X0, Y0, X1, Y1 = [round(v * 1.5) for v in (x0 - 3, yy0 - 3, x1 + 3, yy1 + 3)]
    o.rounded_rectangle((X0, Y0, X1, Y1), radius=12, outline=(224, 0, 21), width=6)
out.save(OUT)
print('saved', OUT, out.size)
