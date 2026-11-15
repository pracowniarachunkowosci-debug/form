"""Read-only checks for the internal legal HTML packet; writes only qa/links.json."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json

ROOT = Path(__file__).resolve().parent
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.errors, self.stack = set(), [], [], []
        self.noindex = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if tag in {'script', 'form', 'iframe', 'input', 'button'}:
            self.errors.append('Unexpected interactive/external-capable element: ' + tag)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append('Duplicate id: ' + attrs['id'])
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.refs.append(attrs[key])
                if key == 'src' and urlsplit(attrs[key]).scheme:
                    self.errors.append('Remote resource: ' + attrs[key])
        if tag == 'meta' and attrs.get('name') == 'robots':
            self.noindex = 'noindex' in attrs.get('content', '')
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append('Unbalanced closing tag: ' + tag)
        else:
            self.stack.pop()

docs, errors, refs = {}, [], 0
for path in sorted(ROOT.glob('*.html')):
    content = path.read_text(encoding='utf-8')
    doc = Document()
    doc.feed(content)
    docs[path] = doc
    if not doc.noindex or 'DO AKCEPTACJI / NIEPUBLIKOWANE' not in content:
        errors.append(f'{path.name}: missing draft/noindex notice')
    errors.extend(f'{path.name}: {error}' for error in doc.errors)
    if doc.stack:
        errors.append(f'{path.name}: unclosed tags {doc.stack}')
for path, doc in docs.items():
    for value in doc.refs:
        url = urlsplit(value)
        if url.scheme or url.netloc:
            continue
        refs += 1
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if not target.is_file():
            errors.append(f'{path.name}: missing {value}')
        if url.fragment and target in docs and unquote(url.fragment) not in docs[target].ids:
            errors.append(f'{path.name}: missing anchor {value}')
result = {'status': 'FAIL' if errors else 'PASS', 'html_files': len(docs),
          'local_references': refs, 'checks': ['HTML nesting', 'unique IDs', 'local links/fragments',
          'draft marker/noindex', 'no scripts/forms/iframes/remote src'], 'errors': errors}
(ROOT / 'qa').mkdir(exist_ok=True)
(ROOT / 'qa' / 'links.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(bool(errors))
