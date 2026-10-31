# 신분증 복사 그림 만들기 — 2026-10-31
#  - images/copy/copy-id.png: 2017 설명서 화면(video/manual_2017/m17)이 지금 기계와 배치가 같아서 바탕으로 씀
#    안드로이드 바 잘라내고 70원으로 고치고 ①②③ 번호 + [여권] ✕ 표시
#    → 영어·중국어: python -I i18n/screens/make_screens.py images/copy/copy-id.png
#  - images/copy/copy-id-more.png(_en, _zh): 추가 스캔 창을 직접 그림 (글자는 매장 사진 D:\클로드\복합기화면사진\정리 그대로)
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, 'video', 'manual_2017', 'm17_신분증복사.png')
OUT = os.path.join(ROOT, 'images', 'copy')
BOLD = r'C:\Windows\Fonts\malgunbd.ttf'
RED = (224, 0, 21)
FONTS = {'ko': (r'C:\Windows\Fonts\malgun.ttf', BOLD),
         'en': (r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\segoeuib.ttf'),
         'zh': (r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\msyhbd.ttc')}

def badge(d, cx, cy, text, r=20):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED, outline=(255, 255, 255), width=3)
    d.text((cx, cy - 1), text, font=ImageFont.truetype(BOLD, int(r * 1.25)), fill='white', anchor='mm')

def screen():
    im = Image.open(SRC).convert('RGB')
    d = ImageDraw.Draw(im)
    d.rectangle((796, 122, 830, 150), fill=(0, 0, 0))                # 10 → 70
    d.text((829, 136), '70', font=ImageFont.truetype(BOLD, 24), fill=(255, 235, 59), anchor='rm')
    out = im.crop((0, 30, 960, 564)).resize((1440, 801), Image.LANCZOS)
    o = ImageDraw.Draw(out)
    o.rounded_rectangle((286, 148, 576, 212), radius=8, outline=RED, width=6)    # ① [신분증 복사] 탭
    badge(o, 548, 180, '1')
    o.rounded_rectangle((26, 402, 546, 470), radius=8, outline=RED, width=6)     # ② [컬러] [흑백]
    badge(o, 196, 384, '2')
    o.ellipse((1228, 648, 1360, 780), outline=RED, width=6)                      # ③ [시작]
    badge(o, 1206, 714, '3')
    o.rounded_rectangle((286, 538, 546, 603), radius=8, outline=RED, width=6)    # [여권] 누르지 않기
    o.ellipse((520, 518, 568, 566), fill=RED, outline=(255, 255, 255), width=3)
    o.line((533, 531, 555, 553), fill='white', width=6)
    o.line((555, 531, 533, 553), fill='white', width=6)
    out.save(os.path.join(OUT, 'copy-id.png'), optimize=True)

MORE = {
    'ko': ('추가 스캔', '다른 페이지를 스캔하시겠습니까?', '아니오', '예', '앞면만 복사', '뒷면도 복사'),
    'en': ('Scan More', 'Do you want to scan another page?', 'No', 'Yes', 'Front only', 'Back side too'),
    'zh': ('扫描更多', '要扫描另一页吗?', '否', '是', '只复印正面', '背面也复印'),
}

def more(lang):
    title, q, no, yes, no_tip, yes_tip = MORE[lang]
    reg, bold = FONTS[lang]
    W, H = 1200, 640
    im = Image.new('RGB', (W, H), (70, 78, 92))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 120, 30, 1080, 520
    d.rectangle((x0, y0, x1, y1), fill=(248, 249, 250), outline=(205, 210, 216), width=2)
    d.rectangle((x0, y0, x1, y0 + 78), fill=(30, 136, 229))
    d.text((x0 + 34, y0 + 39), title, font=ImageFont.truetype(reg, 36), fill='white', anchor='lm')
    cx = W // 2                                                       # 종이 뭉치 그림
    for i, c in enumerate(((203, 222, 240), (222, 234, 246), (240, 246, 252))):
        dy = (2 - i) * 13
        d.polygon([(cx - 56, 175 + dy), (cx + 56, 175 + dy), (cx + 70, 275 + dy), (cx - 70, 275 + dy)], fill=c, outline=(150, 175, 200))
    d.text((cx, 348), q, font=ImageFont.truetype(reg, 34), fill=(50, 54, 60), anchor='mm')
    f = ImageFont.truetype(reg, 34)
    for bx0, bx1, t in ((x0 + 16, cx - 8, no), (cx + 8, x1 - 16, yes)):
        d.rectangle((bx0, 424, bx1, 504), fill=(255, 255, 255), outline=(175, 180, 188), width=2)
        d.text(((bx0 + bx1) // 2, 464), t, font=f, fill=(40, 44, 50), anchor='mm')
        d.rounded_rectangle((bx0 - 6, 418, bx1 + 6, 510), radius=8, outline=RED, width=6)
    tf = ImageFont.truetype(bold, 34)
    for tx, t in (((x0 + 16 + cx - 8) // 2, no_tip), ((cx + 8 + x1 - 16) // 2, yes_tip)):
        d.text((tx, 578), t, font=tf, fill=(255, 226, 90), anchor='mm')
    name = 'copy-id-more.png' if lang == 'ko' else f'copy-id-more_{lang}.png'
    im.save(os.path.join(OUT, name), optimize=True)

screen()
for lang in MORE:
    more(lang)
print('ok')
