import os
import pathlib
import hashlib
import pickle
from pathlib import Path

original_hou_plus_sprites_folder = 'Higurashi Hou Plus Sprites'

hou_plus_mapping_filename = 'hou_plus_sha256.pickle'
mapped_sprites_folder = 'mapped_sprites'

current_mod_sprites_folder_path = 'current_mod_sprites'

def sha256sum(filename):
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def caculate_hou_plus_sha256():

    mapping = {}

    # iterate through all original hou sprites and calculate their SHA256
    for path in pathlib.Path(original_hou_plus_sprites_folder).rglob('*.*'):
        sha256 = sha256sum(path)
        relpath = path.relative_to(original_hou_plus_sprites_folder)

        mapping[sha256] = str(relpath)
        # out.write(f"{relpath}|{sha256}\n")

    return mapping


def generate_mapping():
    # Enable this line to re-calculate the sh256 of each hou plus sprite
    # with open(hou_plus_mapping_filename, 'wb') as out:
    #     pickle.dump(caculate_hou_plus_sha256(), out)

    with open(hou_plus_mapping_filename, 'rb') as mapping:
        hou_plus_sha256_to_filename = pickle.load(mapping) #type: dict[str, str]


    for path in pathlib.Path(mapped_sprites_folder).rglob('*.*'):
        
        sha256 = sha256sum(path)

        if sha256 in hou_plus_sha256_to_filename:
            original_path = hou_plus_sha256_to_filename[sha256]
            print(f"MAPPED {path} -> {original_path}")
        else:
            print(f"MISSING {path} -> NO MATCH")


def get_current_mod_sprite_paths():
    return [p.relative_to(current_mod_sprites_folder_path) for p in pathlib.Path(current_mod_sprites_folder_path).rglob('*.*')]


# Check every existing sprite has a corresponding mapped sprite
# And check that there are no extra mapped sprites
def cross_check_paths(current_sprite_paths):

    # Check every existing sprite has a corresponding mapped sprite
    for relpath in current_sprite_paths:
        expected_mapped_path = Path(mapped_sprites_folder).joinpath(relpath)
        if os.path.exists(expected_mapped_path):
            print(f"Path {relpath} exists on both sides!")
        else:
            print(f"WARNING: Path {relpath} does not exist at {expected_mapped_path}")

    


# generate_mapping()

current_mod_sprite_paths = get_current_mod_sprite_paths()

cross_check_paths(current_mod_sprite_paths)

# print(current_mod_sprite_paths)

# print(hou_plus_filename_to_sha256)

# Save to file for future use




# serialize 2

# get a copy of existing OG sprites, put each in a folder

# scan all of them to get the required filenames

# save them (make sure to include which chapter each one is from?)



# checking

# Iterate through each chapter

# check each file matched by a corresponding og spirtee

# lookup the sprite in a table to figure out the mapping

# Check for unnecessary files present in mapped sprites