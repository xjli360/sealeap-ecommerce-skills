#!/usr/bin/env python3
"""Validate the shareable repository, not private research or business outcomes."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
COLLECTION = ROOT / "sealeap-amazon-skills"
errors = []
def require(ok, message):
    if not ok:
        errors.append(message)

result = subprocess.run([sys.executable, str(COLLECTION/"validate_collection.py")], capture_output=True, text=True)
try:
    collection_result = json.loads(result.stdout)
except json.JSONDecodeError:
    collection_result = {"ok": False, "errors": ["Collection validator did not return JSON"]}
require(result.returncode == 0, "Collection validation failed")
errors.extend(collection_result.get("errors", []))
catalog = json.loads((COLLECTION/"assets/catalog.json").read_text())
entries = catalog["skills"]
names = {x["name"] for x in entries}
require(len(names) == len(entries), "Duplicate skill names")
require(len(entries) >= 100, "At least 100 skills required")
counts = {p:sum(x["platform"] == p for x in entries) for p in catalog["platforms"]}
require(all(n >= 20 for n in counts.values()), "Each platform needs at least 20 skills")
for e in entries:
    folder = COLLECTION/e["path"]
    text = (folder/"SKILL.md").read_text()
    require(len(text) > 400, "Insufficient task instructions: "+e["name"])
    license_file = folder/"LICENSE"
    require(license_file.is_file() and "Permission is hereby granted" in license_file.read_text(), "Missing MIT permission: "+e["name"])
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if "://" not in target and not target.startswith("#"):
            require((folder/target).is_file(), "Broken entrypoint reference: "+e["name"])

readme = (ROOT/"README.md").read_text()
require(f"Skills-{len(entries)}-" in readme, "README skill badge differs from catalog")
require('src="assets/sealeap-logo.png"' in readme and "https://sealeap.cn" in readme, "Missing SeaLeap logo or website")
require("Copyright (c) 2026 SeaLeap" in (ROOT/"LICENSE").read_text(), "Missing project copyright")
notices = (ROOT/"THIRD_PARTY_NOTICES.md").read_text()
require("Copyright (c) 2026 Nexscope AI" in notices and "THE SOFTWARE IS PROVIDED" in notices, "Missing upstream MIT text")
require((ROOT/"assets/sealeap-logo.png").read_bytes().startswith(bytes.fromhex("89504e470d0a1a0a")), "Logo is not a PNG")

allowed_hosts = {"github.com", "img.shields.io", "sealeap.cn", "help.shopify.com",
    "www.etsy.com", "help.etsy.com", "www.ebay.com", "pages.ebay.com", "export.ebay.com",
    "ads.tiktok.com", "seller-us.tiktok.com", "www.walmartconnect.com",
    "marketplacelearn.walmart.com", "support.google.com", "help.klaviyo.com"}
allowed_github = ("https://github.com/xjli360/sealeap-ecommerce-skills",
    "https://github.com/xjli360/sealeap-amazon-skills",
    "https://github.com/nexscope-ai/eCommerce-Skills")
patterns = {
    "local user path": r"/Users/[A-Za-z0-9_.-]+/",
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "mobile": r"(?<!\d)1[3-9]\d{9}(?!\d)",
    "source video ID": r"\bBV1[0-9A-Za-z]{9}\b",
    "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "credential": r"(?i)(?:api_key|access_token|client_secret|xsec_token)\s*[:=]\s*[\"']?[A-Za-z0-9_-]{16,}"
}
files=[]
for p in ROOT.rglob("*"):
    rel=p.relative_to(ROOT)
    if ".git" in rel.parts or "__pycache__" in rel.parts or p.name==".DS_Store" or not p.is_file():
        continue
    files.append(rel.as_posix())
    require(not p.is_symlink(), "Symlink: "+rel.as_posix())
    if p.suffix==".png":
        require(rel.as_posix()=="assets/sealeap-logo.png", "Unexpected binary image")
        continue
    require(p.suffix not in {".pdf",".zip",".csv",".xlsx",".mp4"}, "Private/raw artifact: "+rel.as_posix())
    try:
        t=p.read_text()
    except UnicodeDecodeError:
        errors.append("Unexpected binary: "+rel.as_posix())
        continue
    for label,pattern in patterns.items():
        require(not re.search(pattern,t), label+": "+rel.as_posix())
    for url in re.findall(r"https?://[^\s<>)\"']+",t):
        host=urlsplit(url).hostname
        require(host in allowed_hosts, "Unapproved URL host: "+rel.as_posix())
        if host=="github.com":
            require(url.startswith(allowed_github), "Unapproved repository URL: "+rel.as_posix())
    targets=re.findall(r"\[[^\]]*\]\(([^)]+)\)",t)
    if p.suffix==".md":
        targets+=re.findall(r'(?:href|src)="([^"]+)"',t)
    for target in targets:
        if "://" in target or target.startswith("#"):
            continue
        clean=unquote(target.split("#")[0])
        dest=(p.parent/clean).resolve()
        require(dest.is_relative_to(ROOT), "Link escapes repository: "+rel.as_posix())
        require(dest.exists(), "Broken local link: "+rel.as_posix()+" -> "+target)
output={"ok":not errors,"skills":len(entries),"per_platform":counts,
    "sources":len(json.loads((COLLECTION/"assets/source-register.json").read_text())["sources"]),
    "files":len(files),"errors":errors,"boundary":"Static structure, license, reference and privacy checks; no live seller results."}
print(json.dumps(output,ensure_ascii=False,indent=2))
sys.exit(0 if not errors else 1)

