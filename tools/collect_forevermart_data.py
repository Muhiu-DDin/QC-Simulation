"""Collect low-rate, read-only ForeverMart HTTP checks; never invent measurements.

This checks HTTP availability and the React document shell, not rendered UI flows.
The raw request log is saved so every aggregate CSV row can be independently checked.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import ssl
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://forevermart.vercel.app'
ROUTES = ['/', '/collection', '/about', '/contact', '/cart', '/login', '/orders', '/place-order']


def collect(micro_batches=20, macro_batches=100, delay=.15):
    started = datetime.now(timezone.utc).isoformat()
    context = ssl.create_default_context()
    raw = []
    scale_rows = {}
    for scale, batches in [('micro', micro_batches), ('macro', macro_batches)]:
        rows = []
        for batch in range(batches):
            checks = []
            for attempt in range(3):
                route = '/' if scale == 'micro' else ROUTES[(batch * 3 + attempt) % len(ROUTES)]
                url = BASE_URL + route
                stamp = datetime.now(timezone.utc).isoformat()
                tick = time.perf_counter()
                status = None
                content_type = ''
                content = b''
                error = None
                try:
                    request = Request(url, headers={'User-Agent': 'ForeverMart-Course-QC/1.0', 'Accept': 'text/html'})
                    with urlopen(request, timeout=20, context=context) as response:
                        status = response.status
                        content_type = response.headers.get('Content-Type', '')
                        content = response.read(2_000_000)
                except HTTPError as exc:
                    status = exc.code
                    error = str(exc)
                except (URLError, OSError, TimeoutError) as exc:
                    error = str(exc)
                elapsed = max((time.perf_counter() - tick) * 1000, .001)
                passed = status == 200 and 'text/html' in content_type.lower() and b'id="root"' in content
                item = dict(scale=scale, batch=batch + 1, attempt=attempt + 1, captured_at_utc=stamp,
                            url=url, status=status, content_type=content_type, bytes=len(content),
                            response_ms=elapsed, passed=passed, error=error)
                raw.append(item)
                checks.append(item)
                if delay:
                    time.sleep(delay)
            rows.append(dict(period=f'{scale}-{batch + 1:04d}',
                             passed=sum(x['passed'] for x in checks),
                             failed=sum(not x['passed'] for x in checks),
                             response_ms=sum(x['response_ms'] for x in checks) / len(checks)))
            if (batch + 1) % 10 == 0:
                print(f'{scale}: {batch + 1}/{batches} batches recorded', flush=True)
        scale_rows[scale] = rows
    directory = ROOT / 'data'
    directory.mkdir(exist_ok=True)
    paths = {}
    for scale, rows in scale_rows.items():
        path = directory / f'forevermart_{scale}.csv'
        with path.open('w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['period', 'passed', 'failed', 'response_ms'])
            writer.writeheader()
            writer.writerows(rows)
        paths[scale] = path
    raw_path = directory / 'forevermart_http_checks.json'
    raw_path.write_text(json.dumps(raw, indent=2, allow_nan=False), encoding='utf-8')
    manifest = dict(
        source_url=BASE_URL + '/', captured_at_utc=started,
        completed_at_utc=datetime.now(timezone.utc).isoformat(), synthetic=False,
        method='Sequential read-only HTTPS GET requests; three requests per CSV batch.',
        check_definition='Pass: HTTP 200, HTML content type, and a React root element in the returned document.',
        timing_definition='Client-observed elapsed milliseconds including connection/TLS, network and downloading the HTTP response; not browser rendering or server-only processing time.',
        scope_definition='Micro: repeated homepage checks. Macro: broader checks across eight public page routes. These are relative project scopes, not an industrial Big Data dataset.',
        limitations=[
            'A returned React document shell does not establish that the rendered route, login, cart or checkout works.',
            'Checks are serial observations from one client and one capture window; they are not a concurrency or load test.',
            'Failure counts are failed HTTP checks, not distinct software defects.',
            'A zero observed failure count does not prove that the true failure probability is zero.',
            'The 500 ms threshold in the form is an editable study target, not a verified ForeverMart service-level agreement.',
        ],
        raw_log='data/forevermart_http_checks.json',
        raw_sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        scales={scale: dict(rows=len(rows), checks=sum(r['passed'] + r['failed'] for r in rows),
                            passed=sum(r['passed'] for r in rows), failed=sum(r['failed'] for r in rows),
                            routes=['/'] if scale == 'micro' else ROUTES,
                            csv=f'data/forevermart_{scale}.csv',
                            csv_sha256=hashlib.sha256(paths[scale].read_bytes()).hexdigest())
                for scale, rows in scale_rows.items()})
    directory.joinpath('forevermart_dataset_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest['scales'], indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--micro-batches', type=int, default=20)
    parser.add_argument('--macro-batches', type=int, default=100)
    parser.add_argument('--delay', type=float, default=.15)
    args = parser.parse_args()
    if not 1 <= args.micro_batches <= 1000 or not 1 <= args.macro_batches <= 1000 or args.delay < 0:
        parser.error('Batch counts must be 1..1000 and delay nonnegative.')
    collect(args.micro_batches, args.macro_batches, args.delay)
