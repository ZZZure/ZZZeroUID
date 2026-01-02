import sys
from io import BytesIO
from time import sleep
from pathlib import Path

import httpx
from PIL import Image

sys.path.append(str(Path(__file__).parents[5]))
sys.path.append(str(Path(__file__).parents[2]))

__package__ = "ZZZeroUID.tools"

from ..utils.name_convert import equip_data, weapon_data, partener_data

INTEND_PATH = Path(__file__).parent / "INTEND_RES_PATH"
mask = Image.open(Path(__file__).parent / "texture2d" / "mask.png")

BASE_URL = "https://api.hakush.in/zzz/UI"


def download_url_to_path(url: str, path: Path):
    print(f"正在下载{path.name}")
    print(url)
    while True:
        try:
            char_data = httpx.get(url, follow_redirects=True, timeout=80)
            break
        except:  # noqa:E722
            sleep(4)

    if char_data.status_code != 200:
        print(f"下载{path.name}失败！")
        return

    webp_image = BytesIO(char_data.content)
    img = Image.open(webp_image)

    img.save(path)


def download_suit():
    for equip_id in equip_data:
        equip = equip_data[equip_id]
        equip_name = equip["sprite_file"]
        equip_code_name = equip_name.replace("3D", "")

        URL = f"{BASE_URL}/{equip_code_name}.webp"
        path = INTEND_PATH / "suit" / f"{equip_code_name}.png"
        if path.exists():
            print(f"{equip_code_name}已存在，跳过！")
        else:
            download_url_to_path(URL, path)

        URL2 = f"{BASE_URL}/{equip_name}.webp"
        path2 = INTEND_PATH / "3d_suit" / f"{equip_name}.png"
        if path2.exists():
            print(f"{equip_name}已存在，跳过！")
        else:
            download_url_to_path(URL2, path2)


def download_weapon():
    for weapon_id in weapon_data:
        weapon = weapon_data[weapon_id]
        weapon_code_name = weapon["code_name"]

        URL = f"{BASE_URL}/{weapon_code_name}.webp"
        path = INTEND_PATH / "weapon" / f"{weapon_code_name}_High.png"
        if path.exists():
            print(f"{weapon_code_name}已存在，跳过！")
            continue

        download_url_to_path(URL, path)


def download_IconRoleGeneral():
    for char_id in partener_data:
        partener = partener_data[char_id]
        psprite_id = partener["sprite_id"]

        URL = f"{BASE_URL}/IconRoleGeneral{psprite_id}.webp"
        path = INTEND_PATH / "role_general" / f"IconRoleGeneral{psprite_id}.png"
        if path.exists():
            print(f"{char_id}已存在，跳过！")
        else:
            download_url_to_path(URL, path)

        URL2 = f"{BASE_URL}/IconRoleCircle{psprite_id}.webp"
        path2 = INTEND_PATH / "role_circle" / f"IconRoleCircle{psprite_id}.png"
        if path2.exists():
            print(f"{char_id}已存在，跳过！")
        else:
            download_url_to_path(URL2, path2)

        URL3 = f"{BASE_URL}/IconRole{psprite_id}.webp"
        path3 = INTEND_PATH / "role" / f"IconRole{psprite_id}.png"
        if path3.exists():
            print(f"{char_id}已存在，跳过！")
        else:
            download_url_to_path(URL3, path3)

        for t in [1, 2, 3]:
            URL4 = f"{BASE_URL}/Mindscape_{char_id}_{t}.webp"
            path4 = INTEND_PATH / "mind" / f"Mindscape_{char_id}_{t}.png"
            if path4.exists():
                print(f"{char_id}已存在，跳过！")
            else:
                download_url_to_path(URL4, path4)


def download_bangboo():
    bangboo_list_req = httpx.get("https://api.hakush.in/zzz/data/bangboo.json")
    bangboo_list = bangboo_list_req.json()
    for bangboo_id in bangboo_list:
        icon_name = bangboo_list[bangboo_id]["icon"].split("/")[-1]
        icon_name = icon_name.split(".")[0]
        bangboo_sq_name = f"bangboo_rectangle_avatar_{bangboo_id}.png"
        path = INTEND_PATH / "square_bangbo" / bangboo_sq_name
        if path.exists():
            print(f"{icon_name}已存在，跳过！")
            continue

        URL = f"{BASE_URL}/{icon_name}.webp"
        print(f"正在下载{icon_name}")
        print(URL)
        while True:
            try:
                char_data = httpx.get(URL, follow_redirects=True, timeout=80)
                break
            except:  # noqa:E722
                sleep(4)

        if char_data.headers["Content-Type"] == "image/png":
            img = Image.open(BytesIO(char_data.content))
        elif char_data.headers["Content-Type"] == "image/webp":
            webp_image = BytesIO(char_data.content)
            img = Image.open(webp_image)
        else:
            print(f"{icon_name}不存在，跳过！")
            continue

        im = Image.new("RGBA", (152, 186))
        img = img.resize((268, 268))
        img_temp = im.copy()
        img_temp.paste(img, (-37, -45), img)
        im.paste(img_temp, (0, 0), mask)

        png_bytes = BytesIO()
        im.save(png_bytes, "PNG")
        png_bytes.seek(0)
        char_bytes = png_bytes.read()

        with open(path, "+wb") as handler:
            handler.write(char_bytes)
            print("下载成功！")


if __name__ == "__main__":
    download_weapon()
    download_bangboo()
    download_IconRoleGeneral()
    download_suit()
