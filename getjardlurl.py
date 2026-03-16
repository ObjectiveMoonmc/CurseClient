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
    "Accept": "*/*"
}
async def get_jardlurl(furl):
    async with aiohttp.ClientSession() as session:
        fid_m = re.search(r'/files/(\d+)$', furl)
        if not fid_m:
            return None
        fid = fid_m.group(1)
        resp = await session.get(furl, headers=headers)
        html = await resp.text()
        projid_m = re.search(r'\\?"id\\?":(\d+),\\?"gameId\\?":\d+', html)
        if not projid_m:
            print("e: no projid_m")
            return None
        projid = projid_m.group(1)
        try:
            async with session.get(f"https://www.curseforge.com/api/v1/mods/{projid}/files/{fid}/download", headers=headers, allow_redirects=True) as dlresp:
                return str(dlresp.url)
        except Exception:
            return None