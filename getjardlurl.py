# CurseClient
# Made by ObjectiveMoon
import aiohttp
import re
from urllib.parse import quote
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i",
    "Accept": "*/*"
}
async def get_jardlurl(fileurl, filename=None):
    async with aiohttp.ClientSession() as session:
        filem = re.search(r'/files/(\d+)$', fileurl)
        if not filem:
            return None
        fileid = filem.group(1)
        if filename and filename.lower().endswith(".jar"):
            try:
                part1 = fileid[:4]
                part2 = fileid[4:]
                encodedname = quote(filename)
                return f"https://mediafilez.forgecdn.net/files/{part1}/{part2}/{encodedname}"
            except Exception:
                pass
        resp = await session.get(fileurl, headers=headers)
        data = await resp.text()
        projidm = re.search(r'\\?"id\\?":(\d+),\\?"gameId\\?":\d+', data)
        if not projidm:
            return None
        projid = projidm.group(1)
        apiuri = f"https://www.curseforge.com/api/v1/mods/{projid}/files/{fileid}/download"
        try:
            async with session.get(apiuri, headers={**headers, "Accept": "*/*"}, allow_redirects=False) as r:
                loc1 = r.headers.get("Location", apiuri)
                async with session.get(loc1, headers={**headers, "Accept": "*/*"}, allow_redirects=False) as r:
                    return r.headers.get("Location", loc1)
        except Exception:
            return apiuri