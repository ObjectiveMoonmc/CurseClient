# CurseClient
# Made by ObjectiveMoon
import aiohttp
import re
from getdeps import get_deps_mod
import json
import asyncio
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
async def get_mods_list(query):
    async with aiohttp.ClientSession() as session:
        resp = await session.get("https://www.curseforge.com/minecraft/search", headers=headers, params={"page": "1", "pageSize": "9999", "sortBy": "relevancy", "search": query})
        data = await resp.text()
        cards = re.findall(r'<div class=" project-card">(.*?)</div>\s*<div class=" project-card">', data + '<div class=" project-card">', re.DOTALL)
        pcards = []
        for card in cards:
            name = m.group(1) if (m := re.search(r'class="name"[^>]*><span[^>]*>(.*?)</span>', card)) else ""
            author = m.group(1) if (m := re.search(r'class="author-name"[^>]*><span[^>]*>(.*?)</span>', card)) else ""
            description = m.group(1) if (m := re.search(r'class="description">(.*?)</p>', card)) else ""
            downloads = m.group(1) if (m := re.search(r'class="detail-downloads">(.*?)</li>', card)) else ""
            updated = m.group(1) if (m := re.search(r'class="detail-updated"><span[^>]*>(.*?)</span>', card)) else ""
            gamever = m.group(1) if (m := re.search(r'class="detail-game-version">(.*?)</li>', card)) else ""
            mainmodloader = m.group(1) if (m := re.search(r'class="detail-flavor">(.*?)</li>', card, re.DOTALL)) else ""
            uripath = m.group(1) if (m := re.search(r'class="overlay-link"[^>]*href="([^"]+)"', card)) else ""
            pcards.append((name, author, description, downloads, updated, gamever, mainmodloader, uripath))

        deps = await asyncio.gather(*[
            get_deps_mod(uripath)
            if uripath else asyncio.coroutine(lambda: [])()
            for *_, uripath in pcards
        ])

        mods = []
        for (name, author, description, downloads, updated, gamever, mainmodloader, uripath), deps \
                in zip(pcards, deps):
            mods.append({
                "name": name.strip(),
                "author": author.strip(),
                "description": description.strip(),
                "downloads": downloads.strip(),
                "updated": updated.strip(),
                "gameversion": gamever.strip(),
                "mainmodloader": re.sub(r'<[^>]+>', '', mainmodloader).strip(),
                "dllink": f"https://www.curseforge.com{uripath}",
                "dependencies": deps,
            })

        return json.dumps(mods, indent=2)