# CurseClient
# Made by ObjectiveMoon
import aiohttp
import re
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:155.0) Gecko/20100101 Firefox/155.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Priority": "u=0, i"
}
async def get_deps_mod(modpath):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(f"https://www.curseforge.com{modpath}/relations/dependencies", headers=headers)
        data = await resp.text()
        deps = []
        relations = m.group(1) if (m := re.search(r'relations\\":\[(.*?)\],\\"pagination', data, re.DOTALL)) else ""
        for relation in re.finditer(
            r'\{\\"id\\":\d+,\\"name\\":\\"([^\"]*)\\",\\"slug\\":\\"([^\"]*)\\",'
            r'\\"type\\":\\"[^\"]+\\".*?'
            r'\\"authorName\\":\\"([^\"]*)\\"',
            relations,
            re.DOTALL,
        ):
            name, thing, author = relation.groups()
            deps.append({
                "name": name,
                "author": author,
                "dllink": f"https://www.curseforge.com/minecraft/mc-mods/{thing}",
            })
        return deps