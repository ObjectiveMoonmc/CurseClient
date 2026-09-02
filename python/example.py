# CurseClient
# Made by ObjectiveMoon
from getmodfiles import get_mod_files
from getmodlist import get_mods_list
from getjardlurl import get_jardlurl
import asyncio
async def main():
    print(await get_mods_list(input("Mod to search: ")))
    print(await get_mod_files(input("ModURL: ")))
    print(await get_jardlurl(input("FileURL: ")))
if __name__ == "__main__":
    asyncio.run(main())