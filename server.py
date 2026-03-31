from getmodfiles import get_mod_files
from getmodlist import get_mods_list
from aiohttp import web
async def search(request):
    return web.json_response(await get_mods_list(request.match_info.get('modname')))
async def getdl(request):
    r = await request.json()
    return web.json_response(await get_mod_files(r.get('dlurl')))
app = web.Application()
app.router.add_get('/search/{modname}', search)
app.router.add_post('/getdl', getdl)
web.run_app(app)