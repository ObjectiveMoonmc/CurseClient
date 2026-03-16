# CurseClient
# Made by ObjectiveMoon
import aiohttp
import re
from getjardlurl import get_jardlurl
from getldrfiles import get_ldrfiles
import asyncio
import json
from config import versions
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
ldrids = {
    "Forge":    1,
    "Fabric":   4,
    "NeoForge": 6,
    "Quilt":    5,
}
async def get_mod_files(dllink):
    async with aiohttp.ClientSession() as session:
        base = dllink.rstrip("/")
        tasks = [
            get_ldrfiles(base, version, ldrname, ldrid)
            for version in versions
            for ldrname, ldrid in ldrids.items()
        ]
        results = await asyncio.gather(*tasks)
        seen = set()
        fils = []
        for batch in results:
            for f in batch:
                if f["filename"] not in seen:
                    seen.add(f["filename"])
                    fils.append(f)
        dltsk = [get_jardlurl(f["fileurl"]) for f in fils]
        dluri  = await asyncio.gather(*dltsk)
        for f, dlurl in zip(fils, dluri):
            f["jardlurl"] = dlurl or ""
        return json.dumps(fils, indent=2)