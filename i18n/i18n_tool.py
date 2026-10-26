# 홈페이지 다국어 페이지 만들기 도구
#  - 한국어 페이지(guide-print.html 등)에서 번역할 문장(블록 단위 HTML)을 뽑아 i18n/ko.json 에 모으고
#  - 언어별 번역표(i18n/en.json, zh.json, vi.json: {문장id: 번역 HTML})로 /en/ /zh/ /vi/ 폴더에 번역 페이지를 만든다.
#  - 번역이 없는 문장은 한국어 그대로 두고 목록으로 알려 준다.
# 사용:
#   python -I i18n/i18n_tool.py extract            → i18n/ko.json 갱신 (새 문장 추가)
#   python -I i18n/i18n_tool.py todo en            → 아직 번역 안 된 문장 목록 (i18n/todo_en.json)
#   python -I i18n/i18n_tool.py build en zh vi     → 번역 페이지 만들기
import copy, hashlib, json, os, re, sys
from bs4 import BeautifulSoup, NavigableString, Comment
sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N = os.path.join(ROOT, 'i18n')
PAGES = ['guide.html', 'guide-print.html', 'guide-copy.html', 'guide-scan.html', 'guide-fax.html', 'guide-coat.html', 'guide-bind.html', 'guide-video.html', 'faq.html', 'index.html', 'services.html', 'about.html', 'branches.html', 'community.html']          # 번역할 페이지 (차례로 늘려 감)
LANGS = {'en': ('English', 'en'), 'zh': ('中文', 'zh-Hans'), 'vi': ('Tiếng Việt', 'vi')}
HANGUL = re.compile('[가-힣]')
BLOCK = {'div', 'p', 'li', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
         'section', 'article', 'aside', 'header', 'footer', 'nav', 'main', 'figure', 'figcaption', 'dl', 'dt', 'dd',
         'form', 'details', 'summary', 'blockquote', 'svg', 'g', 'select', 'img',
         'html', 'head', 'body', 'title', 'meta', 'link', 'style', 'script', 'noscript', 'video', 'source', 'iframe', 'canvas', 'hr'}
SKIP = {'script', 'style', 'noscript'}
ATTRS = ['alt', 'title', 'placeholder', 'aria-label', 'content', 'data-label']

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

def sid(s):
    return hashlib.md5(norm(s).encode('utf-8')).hexdigest()[:10]

def has_block_child(el):
    return any(getattr(c, 'name', None) in BLOCK and getattr(c, 'name', None) != 'img' for c in el.descendants)

def units(soup):
    """번역 단위: (요소, 'html') — 안에 블록 요소가 없는 한국어 요소의 innerHTML
                 (요소, '@속성') — 속성 값
                 (글자노드, 'text') — 블록 사이에 홀로 있는 한국어 글자"""
    out = []
    for el in soup.find_all(True):
        if el.name in SKIP or any(p.name in SKIP for p in el.parents):
            continue
        for a in ATTRS:
            v = el.get(a)
            if isinstance(v, str) and HANGUL.search(v):
                if a == 'content' and el.name == 'meta' and el.get('name') not in ('description',) and el.get('property') not in ('og:title', 'og:description'):
                    continue
                out.append((el, '@' + a))
        if el.name in ('svg', 'g'):
            continue
        if el.name == 'text' or el.name == 'tspan' or el.name == 'title':
            if HANGUL.search(el.get_text()) and not el.find(['tspan']):
                out.append((el, 'html'))
            continue
        inner_html = el.decode_contents()
        if not HANGUL.search(el.get_text()):
            continue
        if any(getattr(p, '_unit', False) for p in el.parents) or getattr(el, '_inrun', False):
            continue
        if el.name not in ('svg', 'g', 'img', 'br'):
            if not has_block_child(el):
                el._unit = True
                out.append((el, 'html'))
                continue
        # 블록 자식과 섞여 있으면: 블록 사이의 글자·인라인 요소 묶음(run)을 한 문장으로
        run = []
        def flush():
            if run and HANGUL.search(''.join(x.get_text() if hasattr(x, 'get_text') else str(x) for x in run)):
                for x in run:
                    if hasattr(x, 'find_all'):
                        x._inrun = True
                        for d in x.find_all(True):
                            d._inrun = True
                out.append((list(run), 'run'))
            run.clear()
        for c in list(el.children):
            if isinstance(c, Comment):
                continue
            if isinstance(c, NavigableString) or (getattr(c, 'name', None) not in BLOCK and not has_block_child(c)):
                run.append(c)
            else:
                flush()
        flush()
    return out

def prep(soup):
    # 한국어 페이지 전용 🌐 버튼은 번역 대상이 아니고 외국어 페이지에서 뺀다 (위쪽 언어 바꾸기가 대신함)
    for a in soup.find_all('a', class_='nav-lang'):
        a.decompose()
    return soup

def key_of(node, kind):
    if kind == 'run':
        return ''.join(str(x) for x in node)
    if kind == 'html':
        return node.decode_contents()
    if kind == 'text':
        return str(node)
    return node.get(kind[1:])

def load(name):
    p = os.path.join(I18N, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}

def save(name, data):
    json.dump(data, open(os.path.join(I18N, name), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def extract():
    ko = load('ko.json')
    seen = set()
    for page in PAGES:
        soup = prep(BeautifulSoup(open(os.path.join(ROOT, page), encoding='utf-8').read(), 'html.parser'))
        for node, kind in units(soup):
            k = norm(key_of(node, kind))
            i = sid(k)
            seen.add(i)
            if i not in ko:
                ko[i] = {'ko': k, 'pages': [page]}
            elif page not in ko[i]['pages']:
                ko[i]['pages'].append(page)
    for i in [i for i, v in ko.items() if i not in seen and set(v['pages']) <= set(PAGES)]:
        del ko[i]                          # 원문이 바뀌어 더는 안 쓰는 문장
    save('ko.json', ko)
    print('ko.json', len(ko), 'segments (this run', len(seen), ')')

def todo(lang):
    ko, tr = load('ko.json'), load(lang + '.json')
    t = {i: v['ko'] for i, v in ko.items() if i not in tr}
    save('todo_%s.json' % lang, t)
    print(lang, 'todo', len(t))

# ---------- 번역 페이지 만들기 ----------
URL_ATTRS = [('img', 'src'), ('script', 'src'), ('link', 'href'), ('a', 'href'), ('source', 'src'), ('video', 'poster'),
             ('image', 'href'), ('use', 'href')]

def fix_url(u, lang):
    if not u or u.startswith(('http:', 'https:', '//', '#', 'mailto:', 'tel:', 'data:', 'javascript:')):
        return u
    page = u.split('#')[0].split('?')[0]
    if page in PAGES:                      # 번역된 페이지끼리는 같은 언어 폴더 안에서
        return u
    return '../' + u

def switcher_html(page, cur):
    # 위쪽 메뉴의 언어 고르기 (고르면 바로 그 언어의 같은 페이지로)
    opts = ['<option value="../%s" lang="ko">한국어</option>' % page]
    for k, (label, hl) in LANGS.items():
        sel = ' selected' if k == cur else ''
        opts.append('<option value="../%s/%s" lang="%s"%s>%s</option>' % (k, page, hl, sel, label))
    return ('<label class="lang-sel" title="Language · 语言 · Ngôn ngữ"><span aria-hidden="true">🌐</span>'
            '<span class="cur" aria-hidden="true">%s ▾</span>' % cur.upper() +
            '<select aria-label="Language" onchange="location.href=this.value">' + ''.join(opts) + '</select></label>')

SW_CSS = ('<style>.lang-sel{display:inline-flex;align-items:center;gap:4px;margin-right:8px;border:1.5px solid #1B8AC4;border-radius:50px;'
          'padding:3px 4px 3px 10px;background:#fff;font-size:15px}.lang-sel select{border:none;background:transparent;font:700 13px sans-serif;'
          'color:#1B8AC4;padding:4px 2px;cursor:pointer;outline:none}.nav-links a{padding:8px 11px!important}@media(max-width:1280px){.nav-raccoon{display:none!important}}'
          '.lang-sel .cur{display:none}@media(max-width:480px){.nav-cta{display:none!important}'
          '.lang-sel{position:relative;margin-right:6px;padding:6px 10px;gap:5px}.lang-sel .cur{display:inline;white-space:nowrap;font:700 13px sans-serif;color:#1B8AC4}'
          '.lang-sel select{position:absolute;inset:0;width:100%;opacity:0}}'
          '@media(max-width:400px){.lang-sel{padding:5px 6px!important;gap:2px!important;font-size:13px}.lang-sel .cur{font-size:12px}}'
          '.lang-sw{position:fixed;right:10px;bottom:12px;z-index:400}'
          '.tr-note{max-width:1160px;margin:0 auto;padding:10px 6% 0;font-size:12.5px;color:#9CA3AF}</style>')
NOTE = {'en': 'This page was translated from Korean. If anything looks wrong, please tell us on Naver TalkTalk. Screens on the machines are in Korean — the Korean button names are shown in [brackets].',
        'zh': '本页由韩语翻译而来。如有不准确之处，请通过 Naver TalkTalk 告诉我们。机器屏幕为韩语，韩语按钮名称写在［括号］里。',
        'vi': 'Trang này được dịch từ tiếng Hàn. Nếu có chỗ nào chưa đúng, vui lòng báo cho chúng tôi qua Naver TalkTalk. Màn hình máy là tiếng Hàn — tên nút tiếng Hàn được ghi trong [ngoặc].'}

def build(lang):
    tr = load(lang + '.json')
    label, hl = LANGS[lang]
    outdir = os.path.join(ROOT, lang)
    os.makedirs(outdir, exist_ok=True)
    missing = 0
    for page in PAGES:
        soup = prep(BeautifulSoup(open(os.path.join(ROOT, page), encoding='utf-8').read(), 'html.parser'))
        for node, kind in units(soup):
            k = norm(key_of(node, kind))
            t = tr.get(sid(k))
            if t is None:
                missing += 1
                continue
            if kind == 'html':
                node.clear()
                frag = BeautifulSoup(t, 'html.parser')
                for c in list(frag.contents):
                    node.append(c)
            elif kind == 'run':
                first = node[0]
                frag = BeautifulSoup(' ' + t + ' ', 'html.parser')
                for c in list(frag.contents):
                    first.insert_before(c)
                for x in node:
                    x.extract()
            else:
                node[kind[1:]] = t
        if soup.html:
            soup.html['lang'] = hl
        for s in soup.find_all('script', src=re.compile(r'quickmenu\.js')):   # 퀵메뉴 그림은 한국어 글씨라 외국어 페이지에선 뺌
            s.decompose()
        for tag, attr in URL_ATTRS:
            for el in soup.find_all(tag):
                if el.get(attr):
                    el[attr] = fix_url(el[attr], lang)
        for tag, attr in (('source', 'src'), ('video', 'poster')):   # 그 언어 영상(videos/이름_en.mp4 등)이 있으면 그걸로
            for el in soup.find_all(tag):
                u = el.get(attr) or ''
                m = re.match(r'^(\.\./videos/[\w\-]+)(\.mp4|\.jpg)$', u)
                if m and os.path.exists(os.path.join(ROOT, m.group(1)[3:] + '_' + lang + m.group(2))):
                    el[attr] = m.group(1) + '_' + lang + m.group(2)
        for el in soup.find_all(style=True):     # style 안의 url(...)
            el['style'] = re.sub(r"url\((['\"]?)(?!https?:|data:|/)([^)'\"]+)\1\)", lambda m: "url(%s../%s%s)" % (m.group(1), m.group(2), m.group(1)), el['style'])
        canon = soup.find('link', rel='canonical')
        if canon:
            canon['href'] = 'https://www.printshopmini.com/%s/%s' % (lang, page)
        soup.head.append(BeautifulSoup(SW_CSS, 'html.parser'))
        # 페이지 스크립트가 화면에 쓰는 글자 T('...')의 번역표 — 다른 스크립트보다 먼저
        ui = load('ui_%s.json' % lang)
        soup.head.insert(0, BeautifulSoup('<script>window.I18N_LANG=%s;window.I18N_ROOT="../";window.I18N_UI=Object.assign(window.I18N_UI||{},%s);</script>'
                                          % (json.dumps(lang), json.dumps(ui, ensure_ascii=False)), 'html.parser'))
        if page == 'faq.html':                 # FAQ 질문·답은 DB에 있어서 i18n/faq/faq_<언어>.js 번역표를 먼저 불러 둠 (compile_faq.py)
            js = os.path.join(I18N, 'faq', 'faq_%s.js' % lang)
            ver = hashlib.md5(open(js, 'rb').read()).hexdigest()[:8]
            soup.head.append(BeautifulSoup('<script src="../i18n/faq/faq_%s.js?v=%s"></script>' % (lang, ver), 'html.parser'))
        body = soup.body
        sw = BeautifulSoup(switcher_html(page, lang), 'html.parser')
        cta = soup.find(class_='nav-cta')
        if cta:
            cta.insert_before(sw)
        else:                                  # 위쪽 메뉴가 없는 페이지는 오른쪽 아래에 띄움
            box = soup.new_tag('div', attrs={'class': 'lang-sw'})
            box.append(sw)
            body.insert(0, box)
        foot = soup.find('footer')
        note = BeautifulSoup('<p class="tr-note">%s</p>' % NOTE[lang], 'html.parser')
        (foot.insert_before(note) if foot else body.append(note))
        open(os.path.join(outdir, page), 'w', encoding='utf-8').write(str(soup))
    print(lang, 'built', len(PAGES), 'pages, missing', missing)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'extract':
        extract()
    elif cmd == 'todo':
        for l in sys.argv[2:]:
            todo(l)
    elif cmd == 'build':
        for l in sys.argv[2:]:
            build(l)
