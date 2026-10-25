import struct
from pathlib import Path
from PIL import Image

folder = Path(__file__).resolve().parents[2] / "data" / "optical" / "sentinel2"

for f in sorted(folder.glob("*.tiff")):
    print(f"\n==========================================")
    print(f"File: {f.name}")
    print(f"Size: {f.stat().st_size / (1024*1024):.2f} MB")
    
    # Try PIL
    try:
        im = Image.open(f)
        print(f"PIL: Size={im.size}, Mode={im.mode}, Format={im.format}")
        tp = im.tag_v2.get(33922)
        sc = im.tag_v2.get(33550)
        if tp and sc:
            ul_lon, ul_lat = tp[3], tp[4]
            res_x, res_y = sc[0], sc[1]
            lr_lon = ul_lon + im.size[0] * res_x
            lr_lat = ul_lat - im.size[1] * res_y
            print(f"Coordinates: Lon [{ul_lon:.5f} to {lr_lon:.5f}], Lat [{lr_lat:.5f} to {ul_lat:.5f}]")
    except Exception as e:
        print(f"PIL failed: {e}")
        # Inspect raw TIFF header
        with open(f, "rb") as fp:
            hdr = fp.read(16)
            print(f"Header hex: {hdr.hex()}")
