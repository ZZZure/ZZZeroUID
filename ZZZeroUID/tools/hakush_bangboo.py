from io import BytesIO
from time import sleep
from pathlib import Path

import httpx
from PIL import Image

mask = Image.open(Path(__file__).parent / "texture2d" / "mask.png")


def download_bangboo():
    bangboo_list_req = httpx.get("https://api.hakush.in/zzz/data/bangboo.json")
    bangboo_list = bangboo_list_req.json()
    for bangboo_id in bangboo_list:
        icon_name = bangboo_list[bangboo_id]["icon"].split("/")[-1]
        icon_name = icon_name.split(".")[0]
        bangboo_sq_name = f"bangboo_rectangle_avatar_{bangboo_id}.png"
        URL = f"https://api.hakush.in/zzz/UI/{icon_name}.webp"
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

        with open(Path(__file__).parent / bangboo_sq_name, "+wb") as handler:
            handler.write(char_bytes)
            print("下载成功！")


if __name__ == "__main__":
    download_bangboo()
