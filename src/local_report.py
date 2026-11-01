"""Local-only demo data, CSV export, and an offline browser report.

This module never makes network requests. All SQL queries are read-only except
for the explicit synthetic demo builder, and the report omits developer contacts.
"""
import csv
import html
import sqlite3
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from models.AppDetails import AppDetails, Source


COLUMNS = (
    "package_name", "name", "category", "sub_category", "installation_count",
    "average_score", "comment_count", "version", "last_update", "source",
)
MAX_REPORT_ROWS = 1000


def create_demo(db_path: Path) -> int:
    """Create three unmistakably fictional apps in a caller-selected database."""
    examples = (
        ("ir.example.demo.weather", "آب‌وهوای نمونه", "weather", 12000, 4.4, "1.2"),
        ("ir.example.demo.notes", "دفترچهٔ نمونه", "productivity", 5300, 4.1, "2.0"),
        ("ir.example.demo.learn", "آموزش نمونه", "education", 850, 4.8, "0.9"),
    )
    if Path(db_path).exists():
        raise FileExistsError("Demo destination already exists; choose a new --db path")
    for package, name, category, installs, score, version in examples:
        AppDetails(
            package_name=package, name=name, category=category,
            installation_count=installs, average_score=score,
            comment_count=12, version=version, source=Source.BAZAR,
            tags=["DEMO", "synthetic"],
            short_description="Synthetic example; not collected from CafeBazaar.",
        ).save_to_db(str(db_path))
    return len(examples)


def _read_rows(db_path: Path, limit: int = 0) -> List[Dict]:
    path = Path(db_path)
    if not path.is_file():
        raise ValueError("SQLite file does not exist: {}".format(path))
    # Read-only mode: do not create an empty database as a side effect.
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        found = {row[1] for row in connection.execute("PRAGMA table_info(app_details)")}
        missing = set(COLUMNS) - found
        if missing:
            raise ValueError("Database does not contain the expected app_details schema")
        query = "SELECT " + ", ".join(COLUMNS) + " FROM app_details ORDER BY name, package_name"
        if limit:
            rows = connection.execute(query + " LIMIT ?", (limit,)).fetchall()
        else:
            rows = connection.execute(query).fetchall()
    return [dict(row) for row in rows]


def _safe_csv(value) -> str:
    value = "" if value is None else str(value)
    # Protect spreadsheet consumers against formula execution in untrusted names.
    if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        value = "'" + value
    return value


def export_csv(db_path: Path, output: Path) -> int:
    rows = _read_rows(db_path)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow([_safe_csv(row[column]) for column in COLUMNS])
    return len(rows)


def _format_int(value) -> str:
    return format(int(value or 0), ",")


def _format_date(value) -> str:
    try:
        stamp = int(value or 0)
        if stamp <= 0:
            return "نامشخص"
        return datetime.fromtimestamp(stamp, tz=timezone.utc).strftime("%Y-%m-%d")
    except (OverflowError, OSError, TypeError, ValueError):
        return "نامشخص"


def create_report(db_path: Path, output: Path, limit: int = 500) -> int:
    if not 1 <= limit <= MAX_REPORT_ROWS:
        raise ValueError("Report limit must be between 1 and {}".format(MAX_REPORT_ROWS))
    # Fetch only a bounded number of rows for a responsive standalone report.
    rows = _read_rows(db_path, limit + 1)
    truncated = len(rows) > limit
    rows = rows[:limit]
    total = len(rows)
    categories = Counter(str(row.get("category") or "نامشخص") for row in rows)
    installs = sum(int(row.get("installation_count") or 0) for row in rows)
    ratings = [float(row["average_score"]) for row in rows if row.get("average_score")]
    mean = sum(ratings) / len(ratings) if ratings else 0.0

    def e(value):
        return html.escape("" if value is None else str(value), quote=True)

    table_rows = []
    for row in rows:
        table_rows.append(
            '<tr><td class="name"><strong>{}</strong><small dir="ltr">{}</small></td>'
            '<td>{}</td><td class="num">{}</td><td class="num">{:.1f}</td>'
            '<td dir="ltr">{}</td><td dir="ltr">{}</td></tr>'.format(
                e(row.get("name") or "بدون نام"), e(row.get("package_name")),
                e(row.get("category") or "نامشخص"),
                e(_format_int(row.get("installation_count"))),
                float(row.get("average_score") or 0),
                e(row.get("version") or "—"),
                e(_format_date(row.get("last_update"))),
            )
        )
    top_categories = ", ".join(
        "{} ({})".format(e(name), count)
        for name, count in categories.most_common(5)
    ) or "بدون داده"
    cutoff = ('این گزارش تنها {} ردیف نخست را نشان می‌دهد. برای همهٔ داده‌ها از CSV استفاده کنید.'.format(limit)
              if truncated else 'تمام ردیف‌های موجود در این پایگاه داده نمایش داده می‌شوند.')
    # No external assets, tracking, HTTP requests, developer contact details, or
    # unescaped user-controlled HTML. Client-side search reads only the local DOM.
    page = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>CafeBazaar Crawler | گزارش آفلاین</title>
<style>
:root{font-family:Tahoma,"Segoe UI",sans-serif;color:#172538;background:#f3f6fa;font-synthesis:none}
*{box-sizing:border-box}
body{margin:0;min-height:100vh}
main{max-width:1160px;margin:auto;padding:clamp(18px,4vw,48px)}
header{display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap}
.brand{font-size:14px;letter-spacing:.04em;color:#087f78;font-weight:800;direction:ltr}
.tag{font-size:12px;color:#04685f;background:#dcf7ee;padding:8px 12px;border-radius:100px}
h1{font-size:clamp(28px,4vw,44px);letter-spacing:-.04em;margin:26px 0 8px}
.lead{color:#526379;line-height:2;max-width:720px}
.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:28px 0}
.card,.panel{background:white;border:1px solid #e2e8f0;border-radius:18px;box-shadow:0 10px 32px rgba(31,47,71,.035)}
.card{padding:22px}
.card span{color:#627187;font-size:13px;display:block}
.card strong{font-size:clamp(19px,3vw,30px);display:block;direction:ltr;text-align:right;margin-top:8px}
.panel{padding:22px;margin-bottom:20px}
h2{font-size:18px;margin:0 0 12px}
.meta,.foot{color:#68768a;font-size:13px;line-height:2}
.controls{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:18px}
input{font:inherit;min-width:min(100%,320px);padding:12px 16px;border:1px solid #c8d3e1;border-radius:12px;background:#fff;color:inherit}
input:focus-visible{outline:3px solid #56b6aa;outline-offset:2px}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;text-align:right;min-width:660px}
th,td{padding:14px 10px;border-bottom:1px solid #eef1f5;font-size:13px;vertical-align:middle}
th{color:#54647a;font-weight:700;background:#f9fbfd}
td.name strong,td.name small{display:block}
td.name small{font-size:11px;color:#8290a1;margin-top:6px;text-align:right}
.num{font-variant-numeric:tabular-nums}
tr:hover td{background:#f9fcfd}
footer{margin-top:28px;color:#63758b;font-size:12px;line-height:2}
@media(max-width:700px){.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.card{padding:16px}.panel{padding:16px}}
@media(max-width:370px){.stats{grid-template-columns:1fr 1fr}.card strong{font-size:18px}}
</style>
</head>
<body><main>
<header><span class="brand">CAFÉBAZAAR / LOCAL RESEARCH</span><span class="tag">گزارش آفلاین · بدون اتصال اینترنت</span></header>
<h1>گزارش برنامه‌های کافه‌بازار</h1>
<p class="lead">نمای خواندنی از داده‌های پایگاه SQLite محلی شما. تعداد نصب‌ها ممکن است تخمینی باشد و به معنی کاربران فعال نیست.</p>
<section class="stats" aria-label="خلاصه">
<div class="card"><span>برنامه‌های نمایش‌داده‌شده</span><strong>__REPORT_COUNT__</strong></div>
<div class="card"><span>دسته‌بندی‌ها</span><strong>__REPORT_CATEGORIES__</strong></div>
<div class="card"><span>جمع تعداد نصب گزارش‌شده</span><strong>__REPORT_INSTALLS__</strong></div>
<div class="card"><span>میانگین امتیازهای ثبت‌شده</span><strong>__REPORT_MEAN__</strong></div>
</section>
<section class="panel"><h2>دسته‌بندی‌های پرتکرار</h2><p class="meta">__REPORT_TOP__</p><p class="meta">__REPORT_CUTOFF__</p></section>
<section class="panel">
<div class="controls"><h2>فهرست برنامه‌ها</h2><label for="search">جست‌وجوی محلی <input id="search" type="search" placeholder="نام، شناسه یا دسته‌بندی"></label></div>
<div class="scroll"><table id="apps"><thead><tr><th>برنامه / شناسه</th><th>دسته‌بندی</th><th>نصب</th><th>امتیاز</th><th>نسخه</th><th>آخرین به‌روزرسانی</th></tr></thead>
<tbody>__REPORT_ROWS__</tbody></table></div>
<p id="empty" class="meta" role="status" hidden>نتیجه‌ای برای این عبارت پیدا نشد.</p>
</section>
<footer>ایجادشده توسط CafeBazaar Crawler · فایل HTML مستقل و محلی · اطلاعات توسعه‌دهندگان و تماس در این نما نمایش داده نمی‌شوند.</footer>
</main>
<script>
const input=document.getElementById('search');
const rows=Array.from(document.querySelectorAll('#apps tbody tr'));
const empty=document.getElementById('empty');
input.addEventListener('input',()=>{const q=input.value.trim().toLocaleLowerCase();let found=0;for(const row of rows){const ok=row.textContent.toLocaleLowerCase().includes(q);row.hidden=!ok;if(ok)found++;}empty.hidden=found!==0;});
</script>
</body></html>"""
    for token, value in (
        ("__REPORT_COUNT__", e(_format_int(total))),
        ("__REPORT_CATEGORIES__", e(_format_int(len(categories)))),
        ("__REPORT_INSTALLS__", e(_format_int(installs))),
        ("__REPORT_MEAN__", e("{:.1f}".format(mean))),
        ("__REPORT_TOP__", top_categories),
        ("__REPORT_CUTOFF__", e(cutoff)),
        ("__REPORT_ROWS__", "\\n".join(table_rows)),
    ):
        page = page.replace(token, value)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    return total
