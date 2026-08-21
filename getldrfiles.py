# CurseClient
# Made by ObjectiveMoon
import re
from urllib.parse import quote
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
}
async def parser(data, base_url):
    files = []
    match = list(re.finditer(r'<div class=" file-row">(.*?)(?=<div class=" file-row">|</div><div class="files-results-bar files-results-bar--bottom")', data, re.DOTALL))
    if match:
        for match in match:
            row = match.group(1)
            fid = re.search(r'file-details-(\d+)', row)
            name = re.search(r'class="name" title="([^"]+)"', row)
            download = re.search(r'/download/(\d+)', row)
            version_matches = re.findall(r'class="file-row-chip(?: file-row-chip-more)?" title="([^"]+)"', row)
            loader = re.search(r'class="ellipsis">(Forge|Fabric|NeoForge|Quilt)</span>', row)
            size = re.search(r'<div class="row-detail"><div class=" tooltip-wrapper"><span>([^<]+(?:KB|MB|GB))</span>', row)
            downloads = re.search(r'class="row-detail downloads".*?<span class="ellipsis">([^<]+)</span>', row, re.DOTALL)
            uploaded = re.search(r'class="row-detail".*?<span>([A-Z][a-z]{2} \d{1,2}, \d{4})</span>', row, re.DOTALL)
            fid = (fid or download)
            if not fid or not name:
                continue
            files.append({
                "filename": "",
                "versions": version_matches,
                "loaders": [loader.group(1)] if loader else [],
                "uploaded": uploaded.group(1) if uploaded else "",
                "size": size.group(1) if size else "",
                "downloads": downloads.group(1) if downloads else "",
                "fileurl": f"https://www.curseforge.com{base_url[len('https://www.curseforge.com'):].rstrip('/')}/files/{fid.group(1)}",
                "displayname": name.group(1),
            })
        return files

async def get_ldrfiles(session, base_url, page, page_size, headers):
    url = f"{base_url}/files/all?page={page}&pageSize={page_size}&showAlphaFiles=hide"
    resp = await session.get(url, headers=headers)
    data = await resp.text()
    nums = re.findall(r'<li[^>]*>\s*<button>(\d+)</button>\s*</li>', data)
    if not nums:
        nums = re.findall(r'<ul class="page-numbers">(.*?)</ul>', data, re.DOTALL)
        if nums:
            nums = re.findall(r'<button>(\d+)</button>', nums[0])
    pages = max((int(n) for n in nums), default=page)
    fmap: dict[str, str] = {}
    for m in re.finditer(r'\\"id\\":(\d+),\\"fileName\\":\\"([^\\"]+)\\"', data):
        name = m.group(2)
        if name.lower().endswith(".jar"):
            fmap[m.group(1)] = name
    if not fmap:
        for m in re.finditer(r'"id":(\d+),"fileName":"([^"]+)"', data):
            name = m.group(2)
            if name.lower().endswith(".jar"):
                fmap[m.group(1)] = name
    files = await parser(data, base_url)
    for f in files:
        if idmatch := re.search(r'/files/(\d+)$', f["fileurl"]):
            fid = idmatch.group(1)
            if fnamer := fmap.get(fid):
                f["filename"] = fnamer
        if not f["filename"]:
            f["filename"] = f.pop("displayname", "")
        else:
            f.pop("displayname", None)
    return files, pages
