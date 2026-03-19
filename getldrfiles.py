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
async def parser(data):
    files = []
    for row in re.findall(r'<a class="file-row-details"(.*?)</a>', data, re.DOTALL):
        fpath = m.group(1) if (m := re.search(r'href="([^"]+)"', row)) else ""
        filename = m.group(1) if (m := re.search(r'class="name"[^>]*title="([^"]+)"', row)) else ""
        uploaded = m.group(1) if (m := re.search(r'<span><span>(.*?)</span></span>', row)) else ""
        size = m.group(1) if (m := re.search(r'<span>(\d+\.?\d*\s*(?:KB|MB|GB))</span>', row)) else ""
        downloads = m.group(1) if (m := re.search(r'class="ellipsis">(.*?)</span>', row)) else ""
        versions = re.findall(r'<li>([\d.]+)</li>', row)
        loaders = re.findall(r'<li>(Forge|Fabric|NeoForge|Quilt)</li>', row)
        if not loaders:
            span = re.search(r'class="detail-other detail-flavor"[^>]*>(.*?)</div>', row, re.DOTALL)
            if span:
                loaders = re.findall(r'(Forge|Fabric|NeoForge|Quilt)', span.group(1))
        if not filename:
            continue
        files.append({
            "filename":  filename.strip(),
            "versions":  versions,
            "loaders":   loaders,
            "uploaded":  uploaded.strip(),
            "size":      size.strip(),
            "downloads": downloads.strip(),
            "fileurl":   f"https://www.curseforge.com{fpath}",
            "jardlurl":  "",
        })
    return files
async def get_ldrfiles(session, base_url, page, page_size, headers):
    url = f"{base_url}/files/all?page={page}&pageSize={page_size}&showAlphaFiles=hide"
    resp = await session.get(url, headers=headers)
    data = await resp.text()
    nums = re.findall(r'<li class=" "><button>(\d+)</button></li>', data)
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
    files = await parser(data)
    for f in files:
        if idmatch := re.search(r'/files/(\d+)$', f["fileurl"]):
            fid = idmatch.group(1)
            if fnamer := fmap.get(fid):
                f["filename"] = fnamer
                f["jardlurl"] = f"https://mediafilez.forgecdn.net/files/{fid[:4]}/{fid[4:]}/{quote(fnamer)}"
    return files, pages
