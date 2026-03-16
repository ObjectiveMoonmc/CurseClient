# CurseClient
# Made by ObjectiveMoon
import aiohttp
import re
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
async def get_ldrfiles(bseuri, version, ldrname, ldrid, alpha=False):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(f"{bseuri}/files/all?page=1&pageSize=50&showAlphaFiles={"hide" if not alpha else "show"}&version={version}&gameVersionTypeId={ldrid}", headers=headers)
        data = await resp.text()
        files = []
        for row in re.findall(r'<a class="file-row-details"(.*?)</a>', data, re.DOTALL):
            filepath = m.group(1) if (m := re.search(r'href="([^"]+)"', row)) else ""
            filename = m.group(1) if (m := re.search(r'class="name"[^>]*title="([^"]+)"', row)) else ""
            uploaded = m.group(1) if (m := re.search(r'<span><span>(.*?)</span></span>', row)) else ""
            size = m.group(1) if (m := re.search(r'<span>(\d+\.?\d*\s*(?:KB|MB|GB))</span>', row)) else ""
            downloads = m.group(1) if (m := re.search(r'class="ellipsis">(.*?)</span>', row)) else ""
            if not filename:
                continue
            files.append({
                "filename": filename.strip(),
                "version": f"{version}-{ldrname}",
                "uploaded": uploaded.strip(),
                "size": size.strip(),
                "downloads": downloads.strip(),
                "fileurl": f"https://www.curseforge.com{filepath}"
            })
        return files