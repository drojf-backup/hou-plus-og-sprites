import os
import pathlib
import hashlib
import pickle
from pathlib import Path
import shutil
import re
import csv
import subprocess
import time
import traceback

def get_key_from_stem(stem):
    key = stem

    if stem[-1].isdigit():
        key = stem[:-1]

    return key

def call(args, **kwargs):
    print("running: {}".format(args))
    retcode = subprocess.call(args, **kwargs)  # use shell on windows
    if retcode != 0:
        # don't print args here to avoid leaking secrets
        raise Exception("ERROR: The last call() failed with retcode {retcode}")


def tryRemoveTree(path):
    attempts = 5
    for i in range(attempts):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return

        except FileNotFoundError:
            return
        except Exception:
            print(f'Warning: Failed to remove "{path}" attempt {i}/{attempts}')
            traceback.print_exc()

        time.sleep(1)


# From https://stackoverflow.com/questions/22680954/7zip-ultra-lzma2-compression
def sevenZipMakeArchive(input_path, output_filename, cwd=None):
    if cwd is None:
        cwd = os.getcwd()

    output_path = os.path.join(cwd, output_filename)

    if os.path.exists(output_path):
        if os.path.isdir(output_path):
            raise Exception("Error: folder exists with same name as output 7z archive")
        else:
            print(f"!!! Removing {output_path}")
            os.remove(output_path)

    sevenzipwithoutinout = '7za a -t7z -m0=lzma2:d1024m -mx=9 -aoa -mfb=64 -md=512m -ms=on'.split()
    sevenzipcommand = sevenzipwithoutinout + [output_filename, input_path]
    print(f"Calling 7zip as {sevenzipcommand}")

    if cwd is None:
        call(sevenzipcommand)
    else:
        call(sevenzipcommand, cwd=cwd)

current_mod_sprites_folder = 'current_mod_sprites'

# this folder should at least contain every unique sprite - can contain extra sprites though
source_folder = 'out_for_mod_fixed'

output_folder = 'mod_final_manual_minimal'

# first, load a database of all the unique images which we want to put in the mod
# in this case these are the hou+ sprites after being renamed to match the mod, and also with any manually fixed images already applied
duplicate_filename_dict = {}
source_database = {}

for path in Path(source_folder).rglob('*.*'):
    if path.suffix != '.png':
        raise Exception(f"Got non png file {path.suffix}")
    
    # if path.name in duplicate_filename_dict:
    #     print(f"WARNING: found duplicate file {path}")
    # else:
    #     duplicate_filename_dict[path.name] = path
    
    stem = path.stem

    key = get_key_from_stem(stem)

    if key in source_database:
        # print(f"Warning: duplicate key {key} at {path} (orig path: {source_database[key]})")
        pass
    else:
        source_database[key] = path

copy_list = []

for chapter_name in os.listdir(current_mod_sprites_folder):
    print(f"Processing folder {chapter_name}")

    already_seen_keys = {}

    for path in Path(current_mod_sprites_folder).joinpath(chapter_name).rglob('*.*'):
        key = get_key_from_stem(path.stem)

        if 'sprite' in path.parts and key in already_seen_keys:
            # print(f"Skipping {path} as already appears in {chapter_name} as {already_seen_keys[key]}")
            continue

        if 'sprite' in path.parts:
            already_seen_keys[key] = path

        source_path = source_database[key]
        dest_path = path

        parts = dest_path.parts[1:]

        chapter_number = int(parts[0][2])

        dest_path = os.path.join(output_folder, f'HigurashiEp{chapter_number:02}_Data/StreamingAssets/OGSprites', *parts[1:])

        # print(chapter_number, parts)
        print(dest_path)

        copy_list.append((source_path, dest_path))



# # Now see which images we need to generate for our mod
# # But also remove any sprites which are just different expressions since the engine can handle this automatically
# for path in Path(current_mod_sprites_folder).rglob('*.*'):
#     key = get_key_from_stem(path.stem)

#     if key in source_database:
#         source_path = source_database[key]
#         dest_path = path
#         copy_list.append((source_path, dest_path))
#         # print(f"{source_path} -> {dest_path}")
#     else:
#         print(f'ERROR: missing key {key} for {path}')

#     # print(key)

# Reformat the dest path to match the mod format

for (source, dest) in copy_list:
    print(source, dest)

    dest_parent = Path(dest).parent
    os.makedirs(dest_parent, exist_ok=True)
    shutil.copy(source, dest)


for j in range(9):
    i = j + 1
    seven_zip_input_folder = f"HigurashiEp{i:02}_Data"
    output_file = f"hou-ogsprites-ep{i:02}.7z"
    sevenZipMakeArchive(seven_zip_input_folder, output_file, cwd=output_folder)

