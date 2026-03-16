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
    "Priority": "u=0, i"
}
async def get_deps_mod(modpath):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(f"https://www.curseforge.com{modpath}/relations/dependencies", headers=headers)
        data = await resp.text()
        deps = []
        for a in re.findall(r'<a class="related-project-card"(.*?)</a>', data, re.DOTALL):
            path = m.group(1) if (m := re.search(r'href="([^"]+)"', a)) else ""
            name = m.group(1) if (m := re.search(r'<h5[^>]*>(.*?)</h5>', a)) else ""
            author = m.group(1) if (m := re.search(r'class="author-name"[^>]*><span[^>]*>(.*?)</span>', a)) else ""
            deps.append({
                "name": name.strip(),
                "author": author.strip(),
                "dllink": f"https://www.curseforge.com{path}"
            })
        return deps