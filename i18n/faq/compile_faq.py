# FAQ 번역 만들기 — FAQ는 Supabase DB에 있어서 페이지 번역(i18n_tool.py)과 따로 해요.
#  1) python -I i18n/faq/compile_faq.py fetch   → 지금 DB의 FAQ·묶음을 faqs_ko.json / cats_ko.json 으로 받기
#  2) 번역 원고 i18n/faq/tr_faq_*.txt 작성 (아래 형식)
#  3) python -I i18n/faq/compile_faq.py          → faq_en.js / faq_zh.js / faq_vi.js 만들기 (외국어 faq.html 이 불러 씀)
#
# 원고 형식 (#로 시작하는 줄이 표시, 그 밖의 줄은 답 내용):
#   @@12                 ← FAQ id
#   #q en: 질문 번역
#   #a en                ← 다음 표시 줄 전까지가 답 (줄바꿈 그대로, [[...]] 표시는 그대로 두고 설명 글자만 번역)
#   ...
#   @@cat mini           ← 묶음 id
#   #c en: 이름 | 설명
#   @@ui 한국어 문구     ← 화면 문구 (faq.html 의 T('...'))
#   #u en: 번역
#   @@pin en: refund=70  ← 검색어 → 맨 위에 보여 줄 FAQ
#
# 한국어 FAQ를 고치면: fetch → 바뀐 질문만 원고 고치기 → 다시 만들기. 지문(h)이 다른 질문은 외국어 페이지에 한국어로 나와요.
import glob, json, os, re, sys, urllib.request
sys.stdout.reconfigure(encoding="utf-8")

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(D))
LANGS = ['en', 'zh', 'vi']

def fhash(s):
    # faq.html 의 faqHash 와 똑같이 (UTF-16 글자 단위)
    h = 5381
    b = s.encode('utf-16-le')
    for i in range(0, len(b), 2):
        c = b[i] | (b[i + 1] << 8)
        h = ((h * 33) & 0xFFFFFFFF) ^ c
    n, out = h, ''
    while True:
        n, r = divmod(n, 36)
        out = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + out
        if not n:
            return out

def fetch():
    key = re.search(r"SB_KEY='([^']+)'", open(os.path.join(ROOT, 'faq.html'), encoding='utf-8').read()).group(1)
    base = 'https://wbcfciiuiootbdezxfwy.supabase.co/rest/v1/'
    for name, q in (('faqs_ko.json', 'faqs?order=sort_order,id'), ('cats_ko.json', 'inventory_config?key=in.(faq_categories,faq_cat_map)')):
        req = urllib.request.Request(base + q, headers={'apikey': key, 'Authorization': 'Bearer ' + key})
        data = json.load(urllib.request.urlopen(req))
        json.dump(data, open(os.path.join(D, name), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(name, len(data))

def parse():
    T = {l: {'items': {}, 'cats': {}, 'ui': {}, 'pin': {}} for l in LANGS}
    for path in sorted(glob.glob(os.path.join(D, 'tr_faq_*.txt'))):
        kind = key = lang = None
        buf = None
        def flush():
            if buf is not None and kind == 'faq':
                T[lang]['items'].setdefault(key, {})['a'] = '\n'.join(buf).strip('\n')
        for line in open(path, encoding='utf-8').read().split('\n'):
            if line.startswith('@@'):
                flush(); buf = None
                head = line[2:].strip()
                if head.startswith('cat '):
                    kind, key = 'cat', head[4:].strip()
                elif head.startswith('ui '):
                    kind, key = 'ui', head[3:]
                elif head.startswith('pin '):
                    l, rest = head[4:].split(':', 1)
                    for kv in rest.split(','):
                        k, v = kv.split('=')
                        T[l.strip()]['pin'][k.strip()] = int(v)
                    kind = None
                else:
                    kind, key = 'faq', head
                continue
            m = re.match(r'#([qacu]) (en|zh|vi)(?:: ?(.*))?$', line)
            if m:
                flush(); buf = None
                t, lang, text = m.group(1), m.group(2), m.group(3) or ''
                if t == 'q':
                    T[lang]['items'].setdefault(key, {})['q'] = text
                elif t == 'a':
                    buf = []
                elif t == 'c':
                    name, _, desc = text.partition(' | ')
                    T[lang]['cats'][key] = {'name': name.strip(), 'desc': desc.strip()}
                elif t == 'u':
                    T[lang]['ui'][key] = '' if text == '<empty>' else text   # 빈 번역은 <empty> 로 적기
                continue
            if buf is not None:
                buf.append(line)
        flush()
    return T

def build():
    faqs = {str(f['id']): f for f in json.load(open(os.path.join(D, 'faqs_ko.json'), encoding='utf-8'))}
    T = parse()
    for l in LANGS:
        items = {}
        for i, t in T[l]['items'].items():
            if i not in faqs:
                print('★', l, '없는 FAQ id', i); continue
            if not t.get('q') or not t.get('a'):
                print('★', l, i, '질문 또는 답 빠짐'); continue
            ko = faqs[i]
            # [[...]] 표시(그림·링크 주소)가 한국어와 같은지 확인
            marks = lambda s: [re.sub(r'^\[\[warn:.*', '[[warn]]', re.sub(r'\|[^|\]]*\]\]$', ']]', x)) for x in re.findall(r'\[\[[^\]]+\]\]', s)]   # [[warn:글]]·[[go:..|글]] 의 글은 번역됨
            if marks(t['a']) != marks(ko['answer'] or ''):
                print('★', l, i, '[[표시]] 다름', marks(t['a']), marks(ko['answer'] or ''))
            items[i] = {'h': fhash((ko['question'] or '') + '\n' + (ko['answer'] or '')), 'q': t['q'], 'a': t['a']}
        miss = [i for i in faqs if i not in items]
        js = ('window.I18N_LANG=%s;window.I18N_ROOT="../";window.I18N_UI=Object.assign(window.I18N_UI||{},%s);window.I18N_PIN=%s;window.I18N_FAQ=%s;\n' % (
            json.dumps(l), json.dumps(T[l]['ui'], ensure_ascii=False), json.dumps(T[l]['pin'], ensure_ascii=False),
            json.dumps({'items': items, 'cats': T[l]['cats']}, ensure_ascii=False)))
        open(os.path.join(D, 'faq_%s.js' % l), 'w', encoding='utf-8').write(js)
        print(l, 'faq', len(items), 'cats', len(T[l]['cats']), 'ui', len(T[l]['ui']), 'missing', miss)

if __name__ == '__main__':
    fetch() if sys.argv[1:] == ['fetch'] else build()
