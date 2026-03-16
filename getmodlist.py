# CurseClient
# Made by ObjectiveMoon
import aiohttp
import re
from getdeps import get_deps_mod
import json
import asyncio
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
async def get_mods_list(query):
    async with aiohttp.ClientSession() as session:
        params = {
            "page": "1",
            "pageSize": "50",
            "sortBy": "relevancy",
            "search": query
        }
        resp = await session.get("https://www.curseforge.com/minecraft/search", headers=headers, params=params)
        data = await resp.text()
        cards = re.findall(r'<div class=" project-card">(.*?)</div>\s*<div class=" project-card">', data + '<div class=" project-card">', re.DOTALL)
        mods = []
        deptsk = []
        for card in cards:
            name = m.group(1) if (m := re.search(r'class="name"[^>]*><span[^>]*>(.*?)</span>', card)) else ""
            author = m.group(1) if (m := re.search(r'class="author-name"[^>]*><span[^>]*>(.*?)</span>', card)) else ""
            description = m.group(1) if (m := re.search(r'class="description">(.*?)</p>', card)) else ""
            downloads = m.group(1) if (m := re.search(r'class="detail-downloads">(.*?)</li>', card)) else ""
            updated = m.group(1) if (m := re.search(r'class="detail-updated"><span[^>]*>(.*?)</span>', card)) else ""
            ver = m.group(1) if (m := re.search(r'class="detail-game-version">(.*?)</li>', card)) else ""
            modldr = m.group(1) if (m := re.search(r'class="detail-flavor">(.*?)</li>', card, re.DOTALL)) else ""
            urlpath = m.group(1) if (m := re.search(r'class="overlay-link"[^>]*href="([^"]+)"', card)) else ""
            deptsk.append(get_deps_mod(urlpath) if urlpath else asyncio.sleep(0, result=[]))
            mods.append({
                "name": name.strip(),
                "author": author.strip(),
                "description": description.strip(),
                "downloads": downloads.strip(),
                "updated": updated.strip(),
                "gameversion": ver.strip(),
                "mainmodloader": re.sub(r'<[^>]+>', '', modldr).strip(), # The mod shows it's primary modloader, but can also be compiled for other loaders, hence the name "mainmodloader"
                "dllink": f"https://www.curseforge.com{urlpath}",
                "dependencies": None
            })
        for mod, deps in zip(mods, await asyncio.gather(*deptsk)):
            mod["dependencies"] = deps
    return json.dumps(mods, indent=2)
