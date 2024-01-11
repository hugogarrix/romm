from typing import Optional

from config import ROMM_HOST
from config.config_manager import config_manager
from fastapi import APIRouter, HTTPException, Request, status
from handler import dbh
from logger.logger import log
from pydantic import BaseModel
from typing_extensions import TypedDict
from utils.oauth import protected_route

router = APIRouter()

WEBRCADE_SUPPORTED_PLATFORM_SLUGS = [
    "3do",
    "arcade",
    "atari2600",
    "atari5200",
    "atari7800",
    "lynx",
    "wonderswan",
    "wonderswan-color",
    "colecovision",
    "turbografx16--1",
    "turbografx-16-slash-pc-engine-cd",
    "supergrafx",
    "pc-fx",
    "nes",
    "n64",
    "snes",
    "gb",
    "gba",
    "gbc",
    "virtualboy",
    "sg1000",
    "sms",
    "genesis-slash-megadrive",
    "segacd",
    "gamegear",
    "neo-geo-cd",
    "neogeoaes",
    "neogeomvs",
    "neo-geo-pocket",
    "neo-geo-pocket-color",
    "ps",
]

WEBRCADE_SLUG_TO_TYPE_MAP = {
    "atari2600": "2600",
    "atari5200": "5200",
    "atari7800": "7800",
    "lynx": "lnx",
    "turbografx16--1": "pce",
    "turbografx-16-slash-pc-engine-cd": "pce",
    "supergrafx": "sgx",
    "pc-fx": "pcfx",
    "virtualboy": "vb",
    "genesis-slash-megadrive": "genesis",
    "gamegear": "gg",
    "neogeoaes": "neogeo",
    "neogeomvs": "neogeo",
    "neo-geo-cd": "neogeocd",
    "neo-geo-pocket": "ngp",
    "neo-geo-pocket-color": "ngc",
    "ps": "psx",
}


class PlatformSchema(BaseModel):
    slug: str
    fs_slug: str
    igdb_id: Optional[int] = None
    sgdb_id: Optional[int] = None
    name: Optional[str]
    logo_path: str
    rom_count: int

    class Config:
        from_attributes = True


class WebrcadeFeedSchema(TypedDict):
    title: str
    longTitle: str
    description: str
    thumbnail: str
    background: str
    categories: list[dict]


class DeletePlatformResponse(TypedDict):
    msg: str


class PlatformBindingResponse(TypedDict):
    msg: str


@protected_route(router.get, "/platforms", ["platforms.read"])
def platforms(request: Request) -> list[PlatformSchema]:
    """Get platforms endpoint

    Args:
        request (Request): Fastapi Request object

    Returns:
        list[PlatformSchema]: All platforms in the database
    """

    return dbh.get_platforms()


@protected_route(router.get, "/platforms/webrcade/feed", [])
def platforms_webrcade_feed(request: Request) -> WebrcadeFeedSchema:
    """Get webrcade feed endpoint

    Args:
        request (Request): Fastapi Request object

    Returns:
        WebrcadeFeedSchema: Webrcade feed object schema
    """
    platforms = dbh.get_platforms()

    with dbh.session.begin() as session:
        return {
            "title": "RomM Feed",
            "longTitle": "Custom RomM Feed",
            "description": "Custom feed from your RomM library",
            "thumbnail": "https://raw.githubusercontent.com/zurdi15/romm/f2dd425d87ad8e21bf47f8258ae5dcf90f56fbc2/frontend/assets/isotipo.svg",
            "background": "https://raw.githubusercontent.com/zurdi15/romm/release/.github/screenshots/gallery.png",
            "categories": [
                {
                    "title": p.name,
                    "longTitle": f"{p.name} Games",
                    "background": f"{ROMM_HOST}/assets/webrcade/feed/{p.slug.lower()}-background.png",
                    "thumbnail": f"{ROMM_HOST}/assets/webrcade/feed/{p.slug.lower()}-thumb.png",
                    "description": "",
                    "items": [
                        {
                            "title": rom.name,
                            "description": rom.summary,
                            "type": WEBRCADE_SLUG_TO_TYPE_MAP.get(p.slug, p.slug),
                            "thumbnail": f"{ROMM_HOST}/assets/romm/resources/{rom.path_cover_s}",
                            "background": f"{ROMM_HOST}/assets/romm/resources/{rom.path_cover_l}",
                            "props": {"rom": f"{ROMM_HOST}{rom.download_path}"},
                        }
                        for rom in session.scalars(dbh.get_roms(p.slug)).all()
                    ],
                }
                for p in platforms
                if p.slug in WEBRCADE_SUPPORTED_PLATFORM_SLUGS
            ],
        }


@protected_route(router.delete, "/platforms/{slug}", ["platforms.write"])
def delete_platform(request: Request, slug) -> DeletePlatformResponse:
    """Detele platform from database [and filesystem]"""

    platform = dbh.get_platform(slug)
    if not platform:
        error = f"Platform {platform.name} - [{platform.fs_slug}] not found"
        log.error(error)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)

    log.info(f"Deleting {platform.name} [{platform.fs_slug}] from database")
    dbh.delete_platform(platform.slug)

    return {"msg": f"{platform.name} - [{platform.fs_slug}] deleted successfully!"}


@protected_route(router.put, "/config/system/platforms", ["platforms.write"])
async def add_platform_binding(request: Request) -> PlatformBindingResponse:
    """Add platform binding to the configuration"""

    data = await request.form()

    fs_slug = data.get("fs_slug")
    slug = data.get("slug")

    config_manager.add_binding(fs_slug, slug)

    return {"msg": f"{fs_slug} binded to: {slug} successfully!"}


@protected_route(router.patch, "/config/system/platforms", ["platforms.write"])
async def delete_platform_binding(request: Request) -> PlatformBindingResponse:
    """Delete platform binding from the configuration"""

    data = await request.form()

    fs_slug = data.get("fs_slug")

    config_manager.remove_binding(fs_slug)

    return {"msg": f"{fs_slug} bind removed successfully!"}
