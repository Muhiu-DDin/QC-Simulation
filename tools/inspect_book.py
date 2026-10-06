"""Local source inspection; never changes the supplied textbook."""
import argparse
from pathlib import Path
import pymupdf as fitz

parser = argparse.ArgumentParser()
parser.add_argument('pdf')
parser.add_argument('--pages', help='One-based inclusive page range, e.g. 450-490')
parser.add_argument('--render', type=int, help='One-based PDF page to render')
args = parser.parse_args()
doc = fitz.open(args.pdf)
out = Path('tmp/pdfs')
out.mkdir(parents=True, exist_ok=True)
if args.render:
    doc[args.render - 1].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(out / f'page-{args.render}.png')
elif args.pages:
    lo, hi = map(int, args.pages.split('-'))
    text = '\n'.join(f'\n=== PDF PAGE {i+1} ===\n' + doc[i].get_text(sort=True) for i in range(lo-1, hi))
    path = out / f'pages-{lo}-{hi}.txt'
    path.write_text(text, encoding='utf-8')
    print(path)
else:
    print('PDF pages:', len(doc))
    for i, page in enumerate(doc):
        text = page.get_text()
        if 'Quality Control' in text or '10.1' in text or 'CHAPTER 10' in text:
            print(i + 1, text[:250].replace('\n', ' '))
