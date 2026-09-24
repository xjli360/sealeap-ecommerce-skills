#!/usr/bin/env python3
"""Offline structural, evidence-link and public-content checks. No account access."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent
PLATFORMS = {"shopify", "etsy", "ebay", "tiktokshop", "walmart"}
ALLOWED_HOSTS = {
    "github.com", "help.shopify.com", "www.etsy.com", "help.etsy.com",
    "www.ebay.com", "pages.ebay.com", "export.ebay.com",
    "ads.tiktok.com", "seller-us.tiktok.com", "www.walmartconnect.com",
    "marketplacelearn.walmart.com", "support.google.com", "help.klaviyo.com",
}
errors = []
def require(ok, message):
    if not ok:
        errors.append(message)

catalog = json.loads((ROOT / "assets/catalog.json").read_text())
register = json.loads((ROOT / "assets/source-register.json").read_text())
entries = catalog["skills"]
source_rows = register["sources"]
sources = {x["id"]: x for x in source_rows}
require(len(sources) == len(source_rows), "Duplicate source IDs")
require(len(entries) >= 100, "Expected at least 100 skill entries")
require(len({x["name"] for x in entries}) == len(entries), "Duplicate skill names")
require({p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")} == PLATFORMS | {"assets"}, "Unexpected top-level directory")
require({p.parent.relative_to(ROOT).as_posix() for p in ROOT.rglob("SKILL.md")} == {x["path"] for x in entries}, "Catalog and actual skill folders differ")
for platform in sorted(PLATFORMS):
    require(sum(x["platform"] == platform for x in entries) >= 20, "Fewer than 20 skills: " + platform)
    require({x["mode"] for x in entries if x["platform"] == platform} == {"selection", "operations", "advertising"}, "Missing mode: " + platform)

for row in entries:
    folder = ROOT / row["path"]
    require(folder.name == row["name"], "Folder/name mismatch: " + row["name"])
    require(bool(re.fullmatch(r"sealeap-[a-z0-9-]{1,54}", row["name"])), "Invalid name: " + row["name"])
    needed = ["SKILL.md", "agents/openai.yaml", "references/playbook.md", "references/evidence.md", "LICENSE"]
    for rel in needed:
        require((folder / rel).is_file(), "Missing resource: " + row["path"] + "/" + rel)
    text = (folder / "SKILL.md").read_text()
    front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    require(front is not None, "Missing frontmatter: " + row["name"])
    if front:
        pairs = dict(line.split(": ", 1) for line in front.group(1).splitlines() if ": " in line)
        require(pairs.get("name") == row["name"], "Frontmatter name mismatch: " + row["name"])
        require(bool(pairs.get("description")), "Missing description: " + row["name"])
    yaml = (folder / "agents/openai.yaml").read_text()
    require("$" + row["name"] in yaml, "Default prompt missing skill invocation: " + row["name"])
    short = re.search(r'short_description: "([^"]+)"', yaml)
    require(bool(short) and 25 <= len(short.group(1)) <= 64, "UI description length: " + row["name"])
    require(len(row["sources"]) >= 1, "No mapped source: " + row["name"])
    if row.get("topic_reference"):
        require((folder / row["topic_reference"]).is_file(), "Missing topic reference: " + row["name"])
        require(row["topic_reference"] in text, "Undiscoverable topic reference: " + row["name"])
    evidence = (folder / "references/evidence.md").read_text()
    for sid in row["sources"]:
        require(sid in sources, "Unknown source " + sid)
        if sid in sources:
            require(row["name"] in sources[sid]["used_by"], "Missing reverse source mapping: " + sid)
        require(bool(re.search(r"\| " + re.escape(sid) + r" \|", evidence)), "Missing local evidence row: " + sid)
    for f in folder.rglob("*.md"):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", f.read_text()):
            if "://" not in target and not target.startswith("#"):
                dest = (f.parent / unquote(target.split("#")[0])).resolve()
                require(dest.is_relative_to(folder.resolve()), "Skill not independently portable: " + str(f.relative_to(ROOT)))
                require(dest.is_file(), "Broken skill reference: " + str(f.relative_to(ROOT)) + " -> " + target)

for source in source_rows:
    require(bool(source["used_by"]), "Unused accepted source: " + source["id"])
    require(bool(source["engagement_bands"]), "Missing engagement: " + source["id"])
    require(source["metric_verification"] in {"live_public_api", "search_index", "authenticated_browser"}, "Unclear verification mode")
    require(bool(source["content_coverage"]) and bool(source["limitations"]), "Missing source boundary")
    require(not {"url", "author", "handle", "origin_group", "metrics"}.intersection(source), "Private source mapping in public register")

privacy = {
    "local absolute path": r"/Users/[A-Za-z0-9_.-]+/",
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "CN mobile number": r"(?<!\d)1[3-9]\d{9}(?!\d)",
    "session URL token": r"(?i)(?:xsec_token|access_token|refresh_token|cookie)=",
    "video ID": r"\bBV1[0-9A-Za-z]{9}\b",
    "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "credential assignment": r"(?i)(?:api_key|access_token|client_secret)\s*[:=]\s*[\"']?[A-Za-z0-9_-]{16,}",
}
checked = 0
for f in ROOT.rglob("*"):
    if not f.is_file() or f.name in {Path(__file__).name, ".DS_Store"} or f.suffix == ".pyc":
        continue
    require(not f.is_symlink(), "Unexpected symlink: " + str(f.relative_to(ROOT)))
    try:
        content = f.read_text()
    except UnicodeDecodeError:
        errors.append("Unexpected binary file: " + str(f.relative_to(ROOT)))
        continue
    checked += 1
    for label, pattern in privacy.items():
        require(not re.search(pattern, content), label + ": " + str(f.relative_to(ROOT)))
    for url in re.findall(r"https?://[^\s<>)\"']+", content):
        host = urlsplit(url).hostname
        require(host in ALLOWED_HOSTS, "Unapproved source/identity URL: " + str(f.relative_to(ROOT)))
        if host == "github.com":
            require(any(url.startswith(prefix) for prefix in ["https://github.com/xjli360/sealeap-amazon-skills", "https://github.com/nexscope-ai/eCommerce-Skills", "https://github.com/facebookexperimental/Robyn"]), "Unexpected GitHub identity/source mapping")
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
        if "://" not in target and not target.startswith("#"):
            dest = (f.parent / unquote(target.split("#")[0])).resolve()
            require(dest.is_relative_to(ROOT), "Reference escapes collection")
            require(dest.exists(), "Broken relative link: " + str(f.relative_to(ROOT)) + " -> " + target)
    require(not re.search(r"\b(?:TODO|FIXME|PLACEHOLDER)\b", content), "Unfinished scaffold: " + str(f.relative_to(ROOT)))

result = {
    "ok": not errors, "skills": len(entries), "sources": len(sources),
    "checked_text_files": checked, "errors": errors,
    "boundary": "Offline checks only; no authenticated seller flow or business outcome tested",
}
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
