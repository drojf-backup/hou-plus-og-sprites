import os
import pathlib
import hashlib
import pickle
from pathlib import Path
import shutil
import re
import csv

original_hou_plus_sprites_folder = 'Higurashi Hou Plus Sprites'

out_path = 'only_used_hou_sprites'

out_path_with_fixes_for_mod = 'out_for_mod_fixed'

# Remove the topmost folder of the (relative?) path. If there is only one or fewer folder in the path, the path is not changed.
def strip_top_folder(path: str):
    parts = Path(path).parts

    if len(parts) <= 1:
        return path
    else:
        return Path('').joinpath(*(Path(path).parts[1:]))


def copy_used_hou_sprites():
    with open("csv_mapping/mg_to_hou_mapping.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            hou_path_base = row[1]
            fixed_sprite_path = row[2]
            if fixed_sprite_path.strip() == '':
                fixed_sprite_path = None

            if hou_path_base == 'NO_MATCH':
                print(f"Skipping {row}")
                continue

            source = os.path.join(original_hou_plus_sprites_folder, hou_path_base)
            # Use the fixed sprite if available
            if fixed_sprite_path is not None:
                source = fixed_sprite_path

            dest = os.path.join(out_path, strip_top_folder(hou_path_base))
            print(f"Copying {source} to {dest}")

            dest_parent = Path(dest).parent
            os.makedirs(dest_parent, exist_ok=True)
            shutil.copy(source, dest)


def copy_hou_to_mangagamer():
    with open("csv_mapping/mg_to_hou_mapping.csv", newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            mg_relative_path = row[0]
            hou_path_base = row[1]
            fixed_sprite_path = row[2]
            if fixed_sprite_path.strip() == '':
                fixed_sprite_path = None

            if hou_path_base == 'NO_MATCH':
                print(f"Skipping {row}")
                continue

            source = os.path.join(original_hou_plus_sprites_folder, hou_path_base)
            # Use the fixed sprite if available
            if fixed_sprite_path is not None:
                source = fixed_sprite_path

            dest = os.path.join(out_path_with_fixes_for_mod, mg_relative_path)
            print(f"Copying {source} to {dest}")

            dest_parent = Path(dest).parent
            os.makedirs(dest_parent, exist_ok=True)
            shutil.copy(source, dest)

copy_hou_to_mangagamer()