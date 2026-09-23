#!/usr/bin/env python3
# =============================================================================
# job_radar.py
# Fetches economics-PhD-relevant job postings from several employers, keeps only
# the ones that are new since the last run, writes an HTML dashboard, and
# (optionally) emails you a digest of the new postings.
#
# You normally only edit config.py, not this file.
#
# Run it with:   python3 job_radar.py
# =============================================================================

import os                      # to build file paths next to this script
import csv                     # to read/write the "already seen" ledger
import json                    # to parse API responses
import time                    # to pace paginated requests (avoid rate limits)
import smtplib                 # to send the email digest
import datetime as dt          # for timestamps
from email.mime.text import MIMEText            # HTML body of the email
from email.mime.multipart import MIMEMultipart  # to combine body + attachment
from email.mime.application import MIMEApplication  # the dashboard attachment

import requests                # the only third-party library we need

import config                  # your settings from config.py

# --- where files live: always next to this script, regardless of where it's run
HERE      = os.path.dirname(os.path.abspath(__file__))
SEEN_CSV   = os.path.join(HERE, "seen_jobs.csv")   # ledger of everything seen
HTML_OUT   = os.path.join(HERE, "jobs.html")       # the dashboard you open
LAST_EMAIL = os.path.join(HERE, "last_email.txt")  # date we last emailed (once/day)

# A polite browser-like header so servers don't reject us.
HEADERS = {"User-Agent": "Mozilla/5.0 (job_radar personal job monitor)"}
TIMEOUT = 30   # seconds to wait per request before giving up


# =============================================================================
# FETCHERS — one small function per applicant-tracking system.
# Each returns a list of dicts shaped like:
#   {"uid","source","title","location","url","posted"}
# "uid" is a globally-unique id we use to detect duplicates across runs.
# =============================================================================

def fetch_greenhouse(src):
    # Greenhouse exposes a clean public board API. One GET returns every job.
    url = f"https://boards-api.greenhouse.io/v1/boards/{src['slug']}/jobs"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()                       # raise if HTTP error (e.g. 404)
    out = []
    for j in r.json().get("jobs", []):         # loop over each posting
        out.append({
            "uid":      f"greenhouse:{src['slug']}:{j['id']}",
            "source":   src["name"],
            "title":    j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url":      j.get("absolute_url", ""),
            "posted":   (j.get("updated_at") or "")[:10],   # YYYY-MM-DD
        })
    return out


def fetch_smartrecruiters(src):
    # SmartRecruiters paginates 100 at a time; we page until we've got them all.
    out, offset = [], 0
    while True:
        url = (f"https://api.smartrecruiters.com/v1/companies/"
               f"{src['slug']}/postings?limit=100&offset={offset}")
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        for j in data.get("content", []):
            loc = j.get("location", {}) or {}
            out.append({
                "uid":      f"smartrecruiters:{src['slug']}:{j['id']}",
                "source":   src["name"],
                "title":    j.get("name", ""),
                "location": ", ".join(x for x in
                                      [loc.get("city"), loc.get("country")] if x),
                "url":      f"https://jobs.smartrecruiters.com/{src['slug']}/{j['id']}",
                "posted":   (j.get("releasedDate") or "")[:10],
            })
        offset += 100
        if offset >= data.get("totalFound", 0):   # stop once past the last page
            break
    return out


def fetch_lever(src):
    # Lever returns every posting in a single JSON array.
    url = f"https://api.lever.co/v0/postings/{src['slug']}?mode=json"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    out = []
    for j in r.json():
        cat = j.get("categories", {}) or {}
        posted = ""
        if j.get("createdAt"):                 # Lever gives epoch milliseconds
            posted = dt.datetime.utcfromtimestamp(
                j["createdAt"] / 1000).strftime("%Y-%m-%d")
        out.append({
            "uid":      f"lever:{src['slug']}:{j['id']}",
            "source":   src["name"],
            "title":    j.get("text", ""),
            "location": cat.get("location", ""),
            "url":      j.get("hostedUrl", ""),
            "posted":   posted,
        })
    return out


def fetch_workday(src):
    # Workday needs a POST to its "cxs" endpoint; it paginates 20 at a time.
    base = f"https://{src['host']}/wday/cxs/{src['tenant']}/{src['site']}/jobs"
    site_root = f"https://{src['host']}/{src['site']}"
    LIMIT = 20                                 # Workday serves 20 per page max
    out, offset = [], 0
    while offset < 2000:                        # hard safety cap (~100 pages)
        # Workday rate-limits rapid pagination: it returns EMPTY pages (and a
        # bogus total=0) when hit too fast, which would silently truncate us.
        # So we (a) don't trust "total", (b) retry empty pages with backoff,
        # (c) stop only on a short/empty page that survives the retries.
        postings = []
        for attempt in range(4):
            r = requests.post(base,
                              json={"appliedFacets": {}, "limit": LIMIT,
                                    "offset": offset, "searchText": ""},
                              headers={**HEADERS, "Content-Type": "application/json"},
                              timeout=TIMEOUT)
            r.raise_for_status()
            postings = r.json().get("jobPostings", [])
            if postings:
                break
            time.sleep(1.5 * (attempt + 1))    # 1.5s, 3s, 4.5s backoff
        if not postings:                       # empty after retries -> the end
            break
        for j in postings:
            path = j.get("externalPath", "")
            out.append({
                "uid":      f"workday:{src['tenant']}:{path}",
                "source":   src["name"],
                "title":    j.get("title", ""),
                "location": j.get("locationsText", ""),
                "url":      site_root + path,
                "posted":   j.get("postedOn", ""),
                # detail endpoint; used later to fetch the application deadline
                "deadline_url": f"{base}{path}",
            })
        if len(postings) < LIMIT:              # partial page -> last page
            break
        offset += LIMIT
        time.sleep(1.0)                        # pace full-page fetches
    return out


def fetch_workable(src):
    # Workable's public widget endpoint returns the whole board in one GET.
    # Used by the smaller research houses (e.g. Capital Economics).
    url = (f"https://apply.workable.com/api/v1/widget/accounts/"
           f"{src['slug']}?details=true")
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    out = []
    for j in r.json().get("jobs", []):
        loc = j.get("location", {}) or {}
        out.append({
            "uid":      f"workable:{src['slug']}:{j.get('shortcode') or j.get('id')}",
            "source":   src["name"],
            "title":    j.get("title", ""),
            "location": ", ".join(x for x in
                                  [loc.get("city"), loc.get("country")] if x),
            "url":      j.get("url", ""),
            "posted":   (j.get("published_on") or "")[:10],
        })
    return out


# Map each "type" string in config to the function that handles it.
FETCHERS = {
    "greenhouse":      fetch_greenhouse,
    "smartrecruiters": fetch_smartrecruiters,
    "lever":           fetch_lever,
    "workday":         fetch_workday,
    "workable":        fetch_workable,
}


def fetch_deadline(detail_url):
    # Workday job-detail pages expose an application close date. We call this
    # only for the handful of *relevant* Workday jobs, so volume stays tiny.
    # Returns a human string ("15 Jul 2026" / "3 days left") or "" if none.
    try:
        info = requests.get(detail_url, headers=HEADERS,
                            timeout=TIMEOUT).json().get("jobPostingInfo", {})
    except Exception:
        return ""
    end = info.get("endDate")                  # e.g. "2026-07-15"
    left = info.get("timeLeftToApply")         # e.g. "3 days left to apply"
    if end:
        try:
            end = dt.datetime.strptime(end, "%Y-%m-%d").strftime("%d %b %Y")
        except ValueError:
            pass
        return f"{end}" + (f" ({left})" if left else "")
    return left or ""


# =============================================================================
# FILTERING
# =============================================================================

def is_relevant(title, profile):
    # Keep the job only if an INCLUDE word (for this source's profile) is
    # present and no EXCLUDE word is. "consultancy" also keeps Associate/etc.
    t = (title or "").lower()
    if any(bad.lower() in t for bad in config.EXCLUDE):
        return False
    include = {"consultancy": config.INCLUDE_CONSULTANCY,
               "finance":     config.INCLUDE_FINANCE}.get(
                   profile, config.INCLUDE_CORE)
    return any(good.lower() in t for good in include)


def in_locations(location, wanted):
    # Optional per-source geography filter. A source with no "locations" key is
    # unrestricted (so every pre-existing source behaves exactly as before).
    # Postings with a blank location are KEPT: better a stray row than a miss.
    if not wanted:
        return True
    loc = (location or "").lower()
    if not loc.strip():
        return True
    return any(w.lower() in loc for w in wanted)


# =============================================================================
# LEDGER  (the "already seen" memory, stored as a CSV)
# =============================================================================

def load_seen():
    # Return a set of uids we've recorded on any previous run.
    if not os.path.exists(SEEN_CSV):
        return set()
    with open(SEEN_CSV, newline="", encoding="utf-8") as f:
        return {row["uid"] for row in csv.DictReader(f)}


def load_seen_dates():
    # uid -> the date we FIRST recorded it, used to age old rows off the
    # dashboard. Rows stay in the ledger forever: dropping them there would
    # make the radar re-report them as brand new on the next run.
    if not os.path.exists(SEEN_CSV):
        return {}
    out = {}
    with open(SEEN_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                d = dt.date.fromisoformat((row.get("first_seen") or "").strip())
            except ValueError:
                continue                       # malformed date -> treat as ageless
            uid = row["uid"]
            if uid not in out or d < out[uid]:  # keep the earliest sighting
                out[uid] = d
    return out


def append_seen(rows):
    # Add newly-found jobs to the ledger, writing a header if the file is new.
    new_file = not os.path.exists(SEEN_CSV)
    with open(SEEN_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["first_seen", "uid", "source",
                                          "title", "location", "url"])
        if new_file:
            w.writeheader()
        today = dt.date.today().isoformat()
        for j in rows:
            w.writerow({"first_seen": today, "uid": j["uid"],
                        "source": j["source"], "title": j["title"],
                        "location": j["location"], "url": j["url"]})


# =============================================================================
# OUTPUT — HTML dashboard
# =============================================================================

def _category_order(cat):
    # Position of a category in the configured order (unknowns go last).
    try:
        return config.CATEGORY_ORDER.index(cat)
    except ValueError:
        return len(config.CATEGORY_ORDER)


def write_html(all_jobs, new_uids, link_sources, errors):
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    # One section per category (union of categories that have live jobs and/or
    # manual bookmarks), in the configured order. Bookmarks sit INSIDE the
    # category, right under that category's live-jobs table.
    cats = sorted({j.get("category", "Other") for j in all_jobs}
                  | {s.get("category", "Other") for s in link_sources},
                  key=_category_order)
    sections = []
    for cat in cats:
        jobs = [j for j in all_jobs if j.get("category", "Other") == cat]
        # Within a section: new first, then by employer, then title.
        jobs.sort(key=lambda j: (j["uid"] not in new_uids,
                                 j["source"], j["title"]))
        rows = []
        for j in jobs:
            new = j["uid"] in new_uids
            badge = '<span class="new">NEW</span> ' if new else ""
            cls = ' class="newrow"' if new else ""
            deadline = j.get("deadline") or '<span class="roll">rolling / see posting</span>'
            rows.append(
                f'<tr{cls}><td>{badge}<a href="{j["url"]}" target="_blank">'
                f'{_esc(j["title"])}</a></td><td>{_esc(j["source"])}</td>'
                f'<td>{_esc(j["location"])}</td><td>{_esc(j["posted"])}</td>'
                f'<td>{deadline if "roll" in str(deadline) else _esc(deadline)}</td></tr>')

        table_html = (
            f'<table><tr><th>Title</th><th>Employer</th><th>Location</th>'
            f'<th>Posted</th><th>Deadline</th></tr>{"".join(rows)}</table>'
            if rows else '<p class="none">No auto-fetched openings in this category.</p>')

        # This category's manual bookmarks, right under its table.
        links = [s for s in link_sources if s.get("category", "Other") == cat]
        book_html = ""
        if links:
            items = "".join(
                f'<a class="chip" href="{s["url"]}" target="_blank">{_esc(s["name"])} &#8599;</a>'
                for s in links)
            book_html = (f'<div class="book"><span class="booklab">Open manually:'
                         f'</span> {items}</div>')

        sections.append(
            f'<h2>{_esc(cat)} <span class="cnt">{len(jobs)}</span></h2>'
            f'{table_html}{book_html}')

    err_html = ""
    if errors:
        items = "".join(f"<li>{_esc(e)}</li>" for e in errors)
        err_html = (f'<div class="err"><b>Sources that failed this run '
                    f'(will retry next time):</b><ul>{items}</ul></div>')

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Job Radar</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Arial,sans-serif;margin:2rem;color:#0F3D57}}
 h1{{margin-bottom:.2rem}} .sub{{color:#666;margin-bottom:1.4rem}}
 h2{{margin:1.8rem 0 .4rem;padding-bottom:.25rem;border-bottom:3px solid #1668A7;
     font-size:17px}}
 .cnt{{background:#1668A7;color:#fff;font-size:12px;padding:1px 8px;border-radius:9px;
       vertical-align:middle}}
 table{{border-collapse:collapse;width:100%;margin-bottom:.5rem}}
 th,td{{text-align:left;padding:.45rem .6rem;border-bottom:1px solid #e3e3e3;font-size:14px}}
 th{{background:#0F3D57;color:#fff}}
 tr.newrow{{background:#eaf3fb}}
 .new{{background:#1668A7;color:#fff;font-size:11px;padding:1px 6px;border-radius:8px}}
 .roll{{color:#999;font-style:italic}}
 .none{{color:#999;font-size:13px;margin:.2rem 0}}
 a{{color:#1668A7;text-decoration:none}} a:hover{{text-decoration:underline}}
 .book{{margin:.1rem 0 .6rem;font-size:13px}}
 .booklab{{color:#666;font-weight:bold;margin-right:.3rem}}
 .chip{{display:inline-block;background:#eef2f6;border:1px solid #d6dee6;
        border-radius:14px;padding:2px 10px;margin:3px 4px 0 0;color:#0F3D57}}
 .chip:hover{{background:#dce7f2;text-decoration:none}}
 .err{{margin-top:1.2rem;color:#8a1c1c;font-size:13px}}
</style></head><body>
<h1>Job Radar</h1>
<div class="sub">Updated {now} &middot; {len(all_jobs)} matching openings &middot;
 <b>{len(new_uids)} new</b> since last run</div>
{''.join(sections) if sections else '<p>No matching openings right now.</p>'}
{err_html}
</body></html>"""
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html)


def _esc(s):
    # Minimal HTML-escaping so odd characters in titles don't break the page.
    return (str(s or "").replace("&", "&amp;")
            .replace("<", "&lt;").replace(">", "&gt;"))


# =============================================================================
# OUTPUT — email digest of NEW jobs only
# =============================================================================

def send_email(new_jobs):
    cfg = config.EMAIL
    if not cfg.get("ENABLED"):
        return
    if cfg.get("ONLY_WHEN_NEW") and not new_jobs:
        return
    # Only one email per day, even if the workflow runs twice (backup schedule).
    today = dt.date.today().isoformat()
    if os.path.exists(LAST_EMAIL) and open(LAST_EMAIL).read().strip() == today:
        print("  already emailed today — skipping duplicate")
        return
    # Group the new jobs by category, in the configured order.
    cats = sorted({j.get("category", "Other") for j in new_jobs},
                  key=_category_order)
    blocks = []
    for cat in cats:
        items = "".join(
            f'<li><a href="{j["url"]}">{_esc(j["title"])}</a> &mdash; '
            f'{_esc(j["source"])} ({_esc(j["location"])})'
            + (f' &middot; <b>deadline {_esc(j["deadline"])}</b>'
               if j.get("deadline") else "") + '</li>'
            for j in new_jobs if j.get("category", "Other") == cat)
        blocks.append(f"<h4 style='margin:.6em 0 .2em'>{_esc(cat)}</h4><ul>{items}</ul>")
    # In the cloud (GitHub Actions) the secrets come from environment variables
    # so they never sit in the repo; locally they fall back to config.py.
    app_pw = os.environ.get("JOBRADAR_APP_PW", cfg.get("APP_PASSWORD", ""))
    to_field = os.environ.get("JOBRADAR_TO", cfg["TO"])

    new_html = ("".join(blocks) if blocks
                else "<p><i>No new postings since the last check.</i></p>")
    attach = cfg.get("ATTACH_DASHBOARD") and os.path.exists(HTML_OUT)
    note = ("<p>The <b>full dashboard</b> (every current opening, grouped by "
            "category) is attached as <code>jobs.html</code> &mdash; open it in "
            "any browser.</p>" if attach else "")
    html = (f"<h3>{len(new_jobs)} new opening(s) since last check</h3>"
            f"{new_html}<hr>{note}")

    # TO may be one address or a comma-separated list (to share with others).
    recipients = [a.strip() for a in str(to_field).split(",") if a.strip()]
    msg = MIMEMultipart()
    msg["Subject"] = (f"Job Radar — {len(new_jobs)} new; full dashboard attached"
                      if attach else f"Job Radar: {len(new_jobs)} new opening(s)")
    msg["From"] = cfg["FROM"]
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html"))
    if attach:                                 # attach the whole dashboard file
        with open(HTML_OUT, "rb") as f:
            part = MIMEApplication(f.read(), _subtype="html")
        part.add_header("Content-Disposition", "attachment", filename="jobs.html")
        msg.attach(part)
    with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"]) as s:
        s.starttls()
        s.login(cfg["FROM"], app_pw)
        s.sendmail(cfg["FROM"], recipients, msg.as_string())
    with open(LAST_EMAIL, "w") as f:          # record that we emailed today
        f.write(today)
    print(f"  emailed digest to {', '.join(recipients)}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    seen = load_seen()
    all_jobs, link_sources, errors = [], [], []

    for src in config.SOURCES:
        if src["type"] == "link":            # no API: just a dashboard bookmark
            link_sources.append(src)
            continue
        fetcher = FETCHERS.get(src["type"])
        if not fetcher:
            errors.append(f"{src['name']}: unknown type '{src['type']}'")
            continue
        try:
            jobs = fetcher(src)
            profile = src.get("profile", "core")
            wanted_locs = src.get("locations")
            kept = [j for j in jobs
                    if is_relevant(j["title"], profile)
                    and in_locations(j.get("location"), wanted_locs)]
            for j in kept:                    # tag with its category for grouping
                j["category"] = src.get("category", "Other")
            all_jobs.extend(kept)
            print(f"  {src['name']}: {len(kept)} relevant / {len(jobs)} total")
        except Exception as e:               # one bad source must not kill the run
            errors.append(f"{src['name']}: {type(e).__name__}: {e}")
            print(f"  {src['name']}: FAILED ({e})")

    # De-duplicate across sources (same uid could appear twice defensively).
    unique = {j["uid"]: j for j in all_jobs}
    all_jobs = list(unique.values())

    # Fetch application deadlines for the relevant Workday jobs (few of them).
    for j in all_jobs:
        if j.get("deadline_url"):
            j["deadline"] = fetch_deadline(j["deadline_url"])
            time.sleep(0.5)                   # pace to avoid Workday throttling

    # New = anything whose uid we've never recorded before.
    new_jobs = [j for j in all_jobs if j["uid"] not in seen]

    # Age off the dashboard anything we first saw more than MAX_AGE_DAYS ago.
    # These are still live at the employer, but a vacancy we've been staring at
    # for over a month is either filled-but-not-taken-down or not going to be
    # applied for. The ledger keeps them (see load_seen_dates), so they are not
    # re-reported as new; they are just hidden from the page.
    max_age = getattr(config, "MAX_AGE_DAYS", 0)
    stale = 0
    if max_age:
        cutoff = dt.date.today() - dt.timedelta(days=max_age)
        first_seen = load_seen_dates()
        shown = []
        for j in all_jobs:
            d = first_seen.get(j["uid"])
            if d and d < cutoff:
                stale += 1
                continue
            shown.append(j)
        all_jobs = shown

    write_html(all_jobs, {j["uid"] for j in new_jobs}, link_sources, errors)
    append_seen(new_jobs)
    try:
        send_email(new_jobs)
    except Exception as e:
        print(f"  email failed: {e}")

    print(f"\nDone. {len(all_jobs)} matching openings, {len(new_jobs)} new"
          + (f", {stale} aged off (>{max_age}d)" if stale else "") + ".")
    print(f"Dashboard: {HTML_OUT}")


if __name__ == "__main__":
    main()
