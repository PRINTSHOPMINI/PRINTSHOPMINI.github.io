# 번역 원고(i18n/tr_*.txt) → 언어별 번역표(i18n/en.json, zh.json, vi.json)
#  - ko.json 에 없는 id, 빠진 언어, HTML 태그가 한국어 원문과 다른 문장을 알려 준다.
# 사용: python -I i18n/compile_tr.py
import glob, json, os, re, sys

I18N = os.path.dirname(os.path.abspath(__file__))
LANGS = ['en', 'zh', 'vi']
TAG = re.compile(r'<(/?[a-zA-Z0-9]+)((?:\s+[^>]*?)?)\s*/?>')

def tags(s):
    # 태그 이름 + 속성(alt/title 처럼 번역하는 속성은 빼고) 순서
    out = []
    for name, attrs in TAG.findall(s):
        attrs = re.sub(r'\s(alt|title|aria-label)="[^"]*"', '', attrs)
        out.append(name + re.sub(r'\s+', ' ', attrs).strip())
    return out

ko = json.load(open(os.path.join(I18N, 'ko.json'), encoding='utf-8'))
tr = {l: {} for l in LANGS}
for path in sorted(glob.glob(os.path.join(I18N, 'tr_*.txt'))):
    cur = None
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if line.startswith('@@'):
            cur = line[2:].strip()
            if cur not in ko:
                print('★ ko.json 에 없는 id', os.path.basename(path), n, cur)
        elif cur and line[:3] in ('en:', 'zh:', 'vi:'):
            tr[line[:2]][cur] = line[3:].strip()
bad = 0
for l in LANGS:
    for i, t in tr[l].items():
        if i in ko and tags(t) != tags(ko[i]['ko']):
            bad += 1
            print('★ 태그 다름', l, i, '\n   ko', tags(ko[i]['ko']), '\n   ', l, tags(t))
    miss = [i for i in ko if i not in tr[l]]
    if miss:
        print(l, '번역 없음', len(miss), miss[:10])
    json.dump(tr[l], open(os.path.join(I18N, l + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(l, len(tr[l]), 'segments')
print('tag mismatches', bad)
