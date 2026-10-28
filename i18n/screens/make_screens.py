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
 'images/scan/scan-dest.png': [
    ((172, 25, 285, 88), {'en': 'Scan', 'zh': '扫描'}, 44, 'l', 0, (255, 255, 255)),
    ((45, 130, 910, 188), {'en': 'Select the destination to save/send the scanned document.', 'zh': '选择目标以保存/发送已扫描的文档。'}, 34, 'l', 0, None),
    ((1630, 28, 1770, 88), LANG_BTN, 34, 'l', 0, (255, 255, 255)),
    ((1685, 815, 1780, 870), START, 32, 'c', 0, None)],
 'images/scan/scan-options.png': [
    ((1635, 30, 1770, 88), LANG_BTN, 34, 'l', 0, (255, 255, 255)),
    ((45, 135, 660, 192), {'en': 'Load original documents and select scan options.', 'zh': '加载原始文档并选择扫描选项。'}, 34, 'l', 0, None),
    ((58, 252, 210, 296), {'en': 'Original Size', 'zh': '原始大小'}, 32, 'l', 0, None),
    ((50, 612, 290, 655), {'en': 'Original Orientation', 'zh': '原稿方向'}, 32, 'l', 0, None),
    ((62, 668, 378, 732), {'en': 'Upright Images', 'zh': '直立图像'}, 32, 'c', 0, (255, 255, 255)),
    ((402, 668, 720, 732), {'en': 'Sideways Images', 'zh': '侧向图像'}, 32, 'c', 0, None),
    ((50, 788, 130, 830), {'en': 'Duplex', 'zh': '双面'}, 32, 'l', 0, None),
    ((62, 842, 378, 906), {'en': '1 Sided', 'zh': '单面'}, 32, 'c', 0, (255, 255, 255)),
    ((402, 842, 720, 906), {'en': '2 Sided, Book', 'zh': '双面，书本'}, 32, 'c', 0, None),
    ((62, 935, 378, 1000), {'en': '2 Sided, Calendar', 'zh': '双面，日历'}, 30, 'c', 0, None),
    ((818, 250, 975, 300), {'en': 'File Name', 'zh': '文件名'}, 32, 'l', 0, None),
    ((890, 405, 1170, 460), {'en': 'Add Date & Time', 'zh': '添加日期和时间'}, 32, 'l', 0, None),
    ((832, 512, 975, 553), {'en': 'Color Mode', 'zh': '彩色模式'}, 32, 'l', 0, None),
    ((900, 570, 1140, 628), {'en': 'Color', 'zh': '彩色'}, 34, 'c', 0, (255, 255, 255)),
    ((1240, 570, 1480, 628), {'en': 'Mono', 'zh': '单色'}, 34, 'c', 0, None),
    ((832, 690, 975, 733), {'en': 'File Format', 'zh': '文件格式'}, 32, 'l', 0, None),
    ((818, 962, 932, 1012), {'en': 'Resolution', 'zh': '分辨率'}, 32, 'l', 0, None),
    ((1595, 130, 1875, 190), {'en': 'Price per page', 'zh': '每页价格'}, 38, 'c', 0, (255, 255, 255)),
    ((1675, 688, 1795, 738), {'en': 'Reset', 'zh': '重置'}, 34, 'c', 0, (255, 255, 255)),
    ((1696, 830, 1776, 870), START, 34, 'c', 0, (255, 255, 255))],
 'images/fax/fax-options.png': [
    ((160, 20, 262, 85), {'en': 'Fax', 'zh': '传真'}, 44, 'l', 0, (255, 255, 255)),
    ((1640, 28, 1770, 85), LANG_BTN, 32, 'l', 0, (255, 255, 255)),
    ((40, 125, 610, 185), {'en': 'Enter your fax number and select options.', 'zh': '输入传真号码并选择选项。'}, 34, 'l', 0, None),
    ((818, 225, 965, 278), {'en': 'Original Size', 'zh': '原始大小'}, 32, 'l', 1, None),
    ((818, 642, 895, 692), {'en': 'Duplex', 'zh': '双面'}, 32, 'l', 1, None),
    ((825, 708, 1140, 788), {'en': '1 Sided', 'zh': '单面'}, 34, 'c', 0, (255, 255, 255)),
    ((1163, 708, 1480, 788), {'en': '2 Sided, Book', 'zh': '双面，书本'}, 34, 'c', 0, None),
    ((825, 812, 1140, 888), {'en': '2 Sided, Calendar', 'zh': '双面，日历'}, 30, 'c', 0, None),
    ((816, 952, 1040, 1003), {'en': 'Original Orientation', 'zh': '原稿方向'}, 32, 'l', 1, None),
    ((825, 1018, 1140, 1100), {'en': 'Upright Images', 'zh': '直立图像'}, 34, 'c', 0, (255, 255, 255)),
    ((1163, 1018, 1480, 1100), {'en': 'Sideways Images', 'zh': '侧向图像'}, 34, 'c', 0, None),
    ((1600, 125, 1840, 185), {'en': 'Price per page', 'zh': '每页价格'}, 38, 'c', 0, (255, 255, 255)),
    ((1660, 688, 1780, 742), {'en': 'Reset', 'zh': '重置'}, 34, 'c', 0, (255, 255, 255)),
    ((1680, 832, 1765, 885), START, 34, 'c', 0, (255, 255, 255))],
 'images/scan/scan-filename-dpi.png': [
    ((38, 10, 200, 56), {'en': 'File Name', 'zh': '文件名'}, 30, 'l', 0, None),
    ((108, 165, 392, 212), {'en': 'Add Date & Time', 'zh': '添加日期和时间'}, 32, 'l', 0, None),
    ((38, 272, 200, 318), {'en': 'Color Mode', 'zh': '彩色模式'}, 32, 'l', 0, None),
    ((150, 330, 330, 388), {'en': 'Color', 'zh': '彩色'}, 32, 'c', 0, (255, 255, 255)),
    ((480, 330, 660, 388), {'en': 'Mono', 'zh': '单色'}, 32, 'c', 0, None),
    ((38, 452, 200, 497), {'en': 'File Format', 'zh': '文件格式'}, 32, 'l', 0, None),
    ((38, 722, 140, 770), {'en': 'Resolution', 'zh': '分辨率'}, 30, 'l', 0, None)],
 'video/manual_2017/m18_스캔중.png': [
    ((532, 255, 632, 288), {'en': '1 Sided→1 Sided', 'zh': '单面→单面'}, 17, 'l', 0, None),
    ((532, 290, 585, 320), {'en': 'Mono', 'zh': '单色'}, 17, 'l', 0, None),
    ((610, 420, 735, 445), {'en': 'Scanning 0 page(s)', 'zh': '正在扫描 0 页'}, 14, 'r', 0, None),
    ((732, 105, 790, 138), {'en': 'Cancel', 'zh': '取消'}, 22, 'r', 0, (255, 255, 255))],
}

def text_mask(rgb, rect):
    """칸 안에서 바탕과 색이 다른 점(=글자)을 찾는다 — 바탕색은 칸 가장자리 색의 가운데 값 (빨간 안내 테두리는 빼고)"""
    x0, y0, x1, y1 = rect
    box = rgb[y0:y1, x0:x1].astype(int)
    isred = lambda a: (a[..., 0] > 170) & (a[..., 1] < 90) & (a[..., 2] < 100)
    edge = np.concatenate([box[0], box[-1], box[:, 0], box[:, -1]])
    edge = edge[~isred(edge)] if (~isred(edge)).sum() > 10 else edge
    bg = np.median(edge, axis=0)
    flat = edge.std(axis=0).max() < 10          # 바탕이 한 가지 색이면 그 색으로 칠하기 (번짐 없음)
    red = isred(box)
    diff = np.abs(box - bg).sum(axis=2)
    m = ((diff > 70) & ~red).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)
    m[red] = 0
    full = np.zeros(rgb.shape[:2], np.uint8)
    full[y0:y1, x0:x1] = m
    ink = box[(diff > 120) & ~red]
    if len(ink):   # 글자 색: 바탕과 가장 많이 다른 쪽 1/4 (가장자리 흐린 점 빼고)
        far = np.abs(ink - bg).sum(axis=1)
        ink = ink[far >= np.percentile(far, 75)]
    col = tuple(int(v) for v in np.median(ink, axis=0)) if len(ink) else (40, 40, 40)
    return full, bg, col, flat

def make(src, items, lang):
    im = Image.open(os.path.join(ROOT, src)).convert('RGB')
    rgb = np.array(im)
    mask = np.zeros(rgb.shape[:2], np.uint8)
    cols = []
    flats = []
    for rect, tr, size, al, bold, color in items:
        m, bg, col, flat = text_mask(rgb, rect)
        (flats.append((m, bg)) if flat else None)
        mask |= m if not flat else 0
        cols.append(color or col)
    out = cv2.inpaint(rgb[:, :, ::-1].copy(), mask, 5, cv2.INPAINT_TELEA)[:, :, ::-1].copy()
    for m, bg in flats:
        out[m > 0] = bg.astype(np.uint8)
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
        x = x0 + 4 if al == 'l' else (x1 - 4 - w if al == 'r' else (x0 + x1 - w) / 2)
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
