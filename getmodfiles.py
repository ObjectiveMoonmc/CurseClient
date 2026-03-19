# CurseClient
# Made by ObjectiveMoon
import aiohttp
from getldrfiles import get_ldrfiles
import asyncio
from getjardlurl import get_jardlurl
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
ldrids = {
    "Forge":    1,
    "Fabric":   4,
    "NeoForge": 6,
    "Quilt":    5,
}
async def get_mod_files(dllink):
    async with aiohttp.ClientSession() as session:
        base = dllink.rstrip("/")
        page_size = 50
        first, totalpages = await get_ldrfiles(session, base, 1, page_size, headers)
        res = await asyncio.gather(*[
            get_ldrfiles(session, base, p, page_size, headers)
            for p in range(2, totalpages + 1)
        ])
        allfiles = first + [f for files, _ in res for f in files]
        seen: set[str] = set()
        uniquefiles: list[dict] = []
        for f in allfiles:
            if f["fileurl"] not in seen:
                seen.add(f["fileurl"])
                uniquefiles.append(f)
        needsres = [f for f in uniquefiles if not f["jardlurl"]]
        if needsres:
            dluri = await asyncio.gather(*[
                get_jardlurl(f["fileurl"], f["filename"])
                for f in needsres
            ])
            for f, url in zip(needsres, dluri):
                f["jardlurl"] = url or ""
        return uniquefiles