import os
import pathlib
import hashlib
import pickle
from pathlib import Path
import shutil

original_hou_plus_sprites_folder = 'Higurashi Hou Plus Sprites'

hou_plus_mapping_filename = 'hou_plus_sha256.pickle'
mapped_sprites_folder = 'mapped_sprites'

current_mod_sprites_folder_path = 'current_mod_sprites'

current_unique_only = 'current_unique_only'

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


def check_missing_mapped_sprites(current_sprite_paths):
    missing_mapped_sprites = []

    # Check every existing sprite has a corresponding mapped sprite
    for relpath in current_sprite_paths:
        expected_mapped_path = Path(mapped_sprites_folder).joinpath(relpath)
        if not os.path.exists(expected_mapped_path):
            print(f"WARNING: Path {relpath} does not exist at {expected_mapped_path}")
            missing_mapped_sprites.append(expected_mapped_path)

    return missing_mapped_sprites

def check_unecessary_sprites():
    unnecessary_mapped_sprites = []

    # Check for extra files in the mapped sprite output
    for path in pathlib.Path(mapped_sprites_folder).rglob('*.*'):
        relpath = path.relative_to(mapped_sprites_folder)
        expected_current_sprite_path = Path(current_mod_sprites_folder_path).joinpath(relpath)

        if not os.path.exists(expected_current_sprite_path):
            print(f"WARNING: Extra unnecessary file at {expected_current_sprite_path}")
            unnecessary_mapped_sprites.append(str(relpath))

    return unnecessary_mapped_sprites

# Check every existing sprite has a corresponding mapped sprite
# And check that there are no extra mapped sprites
def cross_check_paths(current_sprite_paths):
    missing_mapped_sprites = check_missing_mapped_sprites(current_sprite_paths)

    unnecessary_sprites = check_unecessary_sprites()

    print(f"Found {len(missing_mapped_sprites)} missing sprites: {missing_mapped_sprites}")
    print(f"Found {len(unnecessary_sprites)} unnecesasry sprites: {unnecessary_sprites}")

class CurrentSpriteInfo:
    def __init__(self, path, firstChapter, key) -> None:
        self.path = path
        self.firstChapter = firstChapter
        self.key = key

def get_unique_sprites_per_chapter() -> dict[str, CurrentSpriteInfo]:
    chapter_list = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9']
    sprite_dict = {} #type: dict[str, CurrentSpriteInfo]


    for chapter in chapter_list:
        chapter_unique_count = 0

        print(f"-------- {chapter} --------")
        chapter_folder_path = Path(current_mod_sprites_folder_path).joinpath(chapter)

        for path in pathlib.Path(chapter_folder_path).rglob('*.*'):
            relpath = path.relative_to(chapter_folder_path)

            stripped_path = Path(relpath.parent).joinpath(relpath.stem)

            key = str(stripped_path).rstrip("0123456789")

            # print(key)

            if key not in sprite_dict:
                sprite_dict[key] = CurrentSpriteInfo(relpath, chapter, key)
                chapter_unique_count += 1

        print(f"{chapter} has {chapter_unique_count} unique items")

    return sprite_dict



unique_sprite_dict = get_unique_sprites_per_chapter()

for key, info in unique_sprite_dict.items():
    source_path = os.path.join(current_mod_sprites_folder_path, info.firstChapter, info.path)
    dest_path = os.path.join(current_unique_only, info.firstChapter, info.path)

    # print(f"{source_path} -> {dest_path}")
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source_path, dest_path)





# generate_mapping()

# current_mod_sprite_paths = get_current_mod_sprite_paths()

# cross_check_paths(current_mod_sprite_paths)




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