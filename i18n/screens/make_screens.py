# 복합기 화면 그림(한국어)의 글자를 지우고 영어·중국어 글자로 바꿔 쓴 그림 만들기
#  - 복합기 메뉴는 English · 简体中文 만 있음 → 베트남어 페이지·영상은 _en 그림을 씀
#  - 글자는 2026-10-28 매장에서 찍은 실제 영어·중국어 화면 사진(D:\클로드\복합기화면사진\정리) 그대로
#  - 결과: images/<폴더>/<이름>_en.png, _zh.png  (i18n_tool build 와 영상 스크립트가 있으면 자동으로 씀)
# 사용: python -I i18n/screens/make_screens.py [이름…]
import os, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HANGUL = r'C:\Windows\Fonts\malgun.ttf', r'C:\Windows\Fonts\malgunbd.ttf'   # '원' 처럼 화면에 한글로 남는 글자
FONTS = {'en': (r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\segoeuib.ttf'),
         'zh': (r'C:\Windows\Fonts\msyh.ttc', r'C:\Windows\Fonts\msyhbd.ttc')}

# (지울 칸, {언어: 글자}, 글자 크기, 정렬, 굵게, 글자색(None=원래 글자에서 뽑기))
LANG_BTN = {'en': 'English', 'zh': '简体中文'}
START = {'en': 'Start', 'zh': '开始'}
SCREENS = {
 'images/print/print-machine1.png': [
    ((180, 480, 300, 530), {'en': 'Copy', 'zh': '复印'}, 36, 'c', 0, (255, 255, 255)),
    ((478, 480, 578, 530), {'en': 'Print', 'zh': '打印'}, 36, 'c', 0, (255, 255, 255)),
    ((780, 480, 880, 530), {'en': 'Scan', 'zh': '扫描'}, 36, 'c', 0, (255, 255, 255)),
    ((1082, 480, 1182, 530), {'en': 'Fax', 'zh': '传真'}, 36, 'c', 0, (255, 255, 255)),
    ((1145, 40, 1240, 80), LANG_BTN, 26, 'l', 0, None)],
 'images/print/print-machine2.png': [
    ((115, 55, 195, 105), {'en': 'Print', 'zh': '打印'}, 32, 'l', 0, None),
    ((30, 128, 400, 170), {'en': 'Select the location of the file to be printed.', 'zh': '选择要打印文件的位置。'}, 23, 'l', 0, None),
    ((1140, 592, 1205, 632), START, 23, 'c', 0, None),
    ((1105, 58, 1195, 100), LANG_BTN, 24, 'l', 0, None)],
 'images/print/print-serch.png': [
    ((30, 133, 510, 175), {'en': 'Enter the PIN and select your print job.', 'zh': '输入 PIN 并选择打印作业。'}, 23, 'l', 0, None),
    ((898, 198, 1018, 240), {'en': 'Print All', 'zh': '全部打印'}, 22, 'c', 0, (255, 255, 255)),
    ((30, 275, 80, 312), {'en': 'Date', 'zh': '日期'}, 21, 'l', 0, None),
    ((185, 275, 280, 312), {'en': 'Job Name', 'zh': '作业名称'}, 21, 'l', 0, None),
    ((566, 275, 620, 312), {'en': 'Color', 'zh': '彩色'}, 21, 'l', 0, None),
    ((695, 275, 765, 312), {'en': 'Page', 'zh': '页面'}, 21, 'l', 0, None),
    ((810, 275, 862, 312), {'en': 'Copies', 'zh': '份数'}, 21, 'l', 0, None),
    ((923, 275, 975, 312), {'en': 'Size', 'zh': '尺寸'}, 21, 'l', 0, None),
    ((186, 355, 345, 385), {'en': 'Presentation1', 'zh': '演示文稿1'}, 22, 'l', 0, None),
    ((566, 338, 625, 375), {'en': 'Mono', 'zh': '单色'}, 22, 'l', 0, None),
    ((1140, 592, 1205, 632), START, 23, 'c', 0, None),
    ((1103, 60, 1192, 102), LANG_BTN, 24, 'l', 0, None)],
 'images/print/print-price.png': [
    ((30, 130, 510, 172), {'en': 'Enter the PIN and select your print job.', 'zh': '输入 PIN 并选择打印作业。'}, 23, 'l', 0, None),
    ((902, 204, 1014, 233), {'en': 'Print All', 'zh': '全部打印'}, 21, 'c', 0, None),
    ((30, 276, 77, 308), {'en': 'Date', 'zh': '日期'}, 20, 'l', 0, None),
    ((226, 250, 370, 298), {'en': 'Billing Information', 'zh': '开票信息'}, 28, 'l', 0, None),
    ((226, 345, 525, 395), {'en': 'Total Price: 70 원(KRW)', 'zh': '总价： 70 원(KRW)'}, 28, 'l', 1, None),
    ((226, 405, 450, 445), {'en': '1Page(s), Mono, A4', 'zh': '1页, 单色, A4'}, 22, 'l', 0, None),
    ((345, 508, 505, 554), {'en': 'Cancel Job', 'zh': '取消作业'}, 27, 'c', 0, (255, 255, 255)),
    ((835, 508, 925, 554), {'en': 'OK', 'zh': '确定'}, 27, 'c', 0, (255, 255, 255)),
    ((1080, 126, 1268, 170), {'en': 'Price per page', 'zh': '每页价格'}, 24, 'c', 0, None),
    ((1125, 218, 1220, 256), {'en': 'Total Price:', 'zh': '总价：'}, 22, 'c', 0, None),
    ((1140, 592, 1205, 632), START, 23, 'c', 0, None),
    ((1105, 58, 1195, 100), LANG_BTN, 24, 'l', 0, None)],
}

def text_mask(rgb, rect):
    """칸 안에서 바탕과 색이 다른 점(=글자)을 찾는다 — 바탕색은 칸 가장자리 색의 가운데 값"""
    x0, y0, x1, y1 = rect
    box = rgb[y0:y1, x0:x1].astype(int)
    edge = np.concatenate([box[0], box[-1], box[:, 0], box[:, -1]])
    bg = np.median(edge, axis=0)
    diff = np.abs(box - bg).sum(axis=2)
    m = (diff > 70).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)
    full = np.zeros(rgb.shape[:2], np.uint8)
    full[y0:y1, x0:x1] = m
    ink = box[diff > 120]
    col = tuple(int(v) for v in np.median(ink, axis=0)) if len(ink) else (40, 40, 40)
    return full, bg, col

def make(src, items, lang):
    im = Image.open(os.path.join(ROOT, src)).convert('RGB')
    rgb = np.array(im)
    mask = np.zeros(rgb.shape[:2], np.uint8)
    cols = []
    for rect, tr, size, al, bold, color in items:
        m, bg, col = text_mask(rgb, rect)
        mask |= m
        cols.append(color or col)
    out = cv2.inpaint(rgb[:, :, ::-1].copy(), mask, 5, cv2.INPAINT_TELEA)[:, :, ::-1]
    img = Image.fromarray(out)
    d = ImageDraw.Draw(img)
    for (rect, tr, size, al, bold, color), col in zip(items, cols):
        t = tr[lang]
        f = ImageFont.truetype(FONTS[lang][bold], size)
        x0, y0, x1, y1 = rect
        while d.textlength(t, font=f) > (x1 - x0) * 1.9 and size > 12:   # 너무 길면 줄이기 (칸 밖으로 조금은 넘어가도 됨)
            size -= 1; f = ImageFont.truetype(FONTS[lang][bold], size)
        hf = ImageFont.truetype(HANGUL[bold], size)
        runs = [(ch, hf if '가' <= ch <= '힣' else f) for ch in t]   # 한글 글자만 맑은 고딕으로
        w = sum(d.textlength(ch, font=ff) for ch, ff in runs)
        x = x0 + 4 if al == 'l' else (x0 + x1 - w) / 2
        for ch, ff in runs:
            d.text((x, (y0 + y1) / 2), ch, font=ff, fill=col, anchor='lm')
            x += d.textlength(ch, font=ff)
    base, ext = os.path.splitext(src)
    dst = os.path.join(ROOT, base + '_' + lang + '.png')
    img.save(dst, optimize=True)
    return dst

if __name__ == '__main__':
    want = sys.argv[1:]
    for src, items in SCREENS.items():
        if want and not any(w in src for w in want):
            continue
        for lang in ('en', 'zh'):
            print('ok', make(src, items, lang))
