from pathlib import Path
import glob
import os
from PIL import Image



in_path = 'C:\\drojf\\large_projects\\umineko\\hou-plus-og-sprites\\only_used_hou_sprites\\satoko'
out_path = 'C:\\temp\\New folder (172)\\out_satoko_fix'

# if not os.path.exists('out'):
#     os.mkdir(subfolder)

errorlist = []

for file in glob.glob(os.path.join(in_path, "**/*.png"), recursive=True):
    try:
        rel_path = os.path.relpath(file, in_path)
        print(rel_path)

        im = Image.open(file)

        width = im.width
        height = im.height

        background = Image.new('RGBA', (width, height), (0,0,0,255))

        background.paste(im, mask=im)

        out_file = Path(os.path.join(out_path, rel_path))

        os.makedirs(out_file.parent, exist_ok=True)

        background.save(out_file)
    except Exception as e:
        print(f"Error converting file {file}")
        print(e)
        errorlist.append(file)

print(f"{len(errorlist)} files had errors")
