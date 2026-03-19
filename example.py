# CurseClient
# Made by ObjectiveMoon
from getmodfiles import get_mod_files
from getmodlist import get_mods_list
import asyncio
async def main():
    print(await get_mods_list(input("Mod to search: ")))
    print(await get_mod_files(input("Enter DLLinkn: ")))
if __name__ == "__main__":
    asyncio.run(main())