import os
import pathlib
import hashlib
import pickle
from pathlib import Path
import shutil
import re
import csv

original_hou_plus_sprites_folder = 'Higurashi Hou Plus Sprites'

hou_plus_mapping_filename = 'hou_plus_sha256.pickle'
mapped_sprites_folder = 'mapped_sprites'

current_mod_sprites_folder_path = 'current_mod_sprites'

current_unique_only = 'current_unique_only'

final_output_path = 'final_output'

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

# Map hou+ pathnames to Mangagamer Release filenames
# This will allow us to re-process the files later in case something changes.
def generate_mapping():
    # Enable this line to re-calculate the sh256 of each hou plus sprite
    #with open(hou_plus_mapping_filename, 'wb') as out:
    #    pickle.dump(caculate_hou_plus_sha256(), out)

    with open(hou_plus_mapping_filename, 'rb') as mapping:
        hou_plus_sha256_to_filename = pickle.load(mapping) #type: dict[str, str]

    mapping = {} # type: dict[str, str]

    for path in pathlib.Path(mapped_sprites_folder).rglob('*.*'):
        
        sha256 = sha256sum(path)

        if sha256 in hou_plus_sha256_to_filename:
            original_path = hou_plus_sha256_to_filename[sha256]
            print(f"MAPPED mg: {path} -> hou:{original_path}")
            mapping[path] = original_path
        else:
            print(f"MISSING {path} -> NO MATCH")
            mapping[path] = "NO_MATCH"

    return mapping

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

class MappedSpriteInfo:
    def __init__(self, path, key, full_path) -> None:
        self.path = path
        self.key = key
        self.full_path = full_path

def get_key_from_filename(filename_with_ext, remove_portrait_sprite_folder=True):
    filename = Path(filename_with_ext).with_suffix('')

    is_portrait_or_sprite = ('portrait' in filename_with_ext.parts) or ('sprite' in filename_with_ext.parts)
    if not is_portrait_or_sprite:
        # print(f"Key for {filename_with_ext} will just be {filename}")
        return filename

    key = str(filename).rstrip("0123456789")

    if remove_portrait_sprite_folder:
        key = re.sub(r"^((portrait\\)|(sprite\\))", "", key)

    return key

def get_unique_sprites_per_chapter() -> dict[str, CurrentSpriteInfo]:
    chapter_list = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9']
    sprite_dict = {} #type: dict[str, CurrentSpriteInfo]


    for chapter in chapter_list:
        chapter_unique_count = 0

        print(f"-------- {chapter} --------")
        chapter_folder_path = Path(current_mod_sprites_folder_path).joinpath(chapter)

        paths = [p for p in pathlib.Path(chapter_folder_path).rglob('*.*')]

        portrait = []
        other = []

        for path in paths:
            if 'portrait' in str(path):
                portrait.append(path)
            else:
                other.append(path)

        paths = other + portrait

        for path in paths:
            relpath = path.relative_to(chapter_folder_path)

            stripped_path = Path(relpath.parent).joinpath(relpath.stem)

            key = get_key_from_filename(stripped_path)

            # print(key)

            if key not in sprite_dict:
                sprite_dict[key] = CurrentSpriteInfo(relpath, chapter, key)
                chapter_unique_count += 1

        print(f"{chapter} has {chapter_unique_count} unique items")

    return sprite_dict


def build_mapped_sprites_dict():
    chapter_list = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9']
    sprite_dict = {} #type: dict[str, MappedSpriteInfo]


    for chapter in chapter_list:
        chapter_unique_count = 0

        print(f"-------- {chapter} --------")
        chapter_folder_path = Path(mapped_sprites_folder).joinpath(chapter)

        paths = [p for p in pathlib.Path(chapter_folder_path).rglob('*.*')]

        for path in paths:
            relpath = path.relative_to(chapter_folder_path)

            stripped_path = Path(relpath.parent).joinpath(relpath.stem)

            key = get_key_from_filename(stripped_path)

            path_including_chapter = path.relative_to(mapped_sprites_folder)
            # print(f"{key} -> {path_including_chapter}")

            if key not in sprite_dict:
                sprite_dict[key] = MappedSpriteInfo(path_including_chapter, key, full_path=path)
                chapter_unique_count += 1

        print(f"{chapter} has {chapter_unique_count} unique items")

    return sprite_dict

# Remove the topmost folder of the (relative?) path. If there is only one or fewer folder in the path, the path is not changed.
def strip_top_folder(path: str):
    parts = Path(path).parts

    if len(parts) <= 1:
        return path
    else:
        return Path('').joinpath(*(Path(path).parts[1:]))

# Determine which mangagamer sprite goes to which manually mapped hou sprite, using the sh256 of each file
# Write out to a 2 column CSV file, where the first column is the mangagamer filename, and the second column is the houe filename
def map_mangagamer_sprite_to_manually_mapped_hou(out_csv_path):
    mangagamer_to_hou_mapping = generate_mapping()

    with open(out_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting = csv.QUOTE_ALL)

        # writer.writerow(['mangagamer', 'hou'])

        for mg_key, hou_value in mangagamer_to_hou_mapping.items():
            writer.writerow([strip_top_folder(mg_key), strip_top_folder(hou_value)])

map_mangagamer_sprite_to_manually_mapped_hou("mg_to_hou_mapping.csv")

exit(-1)

# Get mapped sprites that apollo has worked on, but mapped by key
mapped_sprites_dict = build_mapped_sprites_dict()

# Get list of existing unique sprites currently used in our mod
unique_sprite_dict = get_unique_sprites_per_chapter()

# Do a sanity check by going through each sprite currently used in our mod,
# And check there is a corresponding mapping to the manually matched sprites
key_missing = False
for key, value in unique_sprite_dict.items():
    if key not in mapped_sprites_dict:
        print(f"Key {key} is missing")
        key_missing = True

if key_missing:
    print("Terminating as some sprites are not matched.")
    exit(-1)

chapter_list = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9']

copy_list = []

for path in pathlib.Path(current_mod_sprites_folder_path).rglob('*.*'):
    rel_path = path.relative_to(current_mod_sprites_folder_path)

    chapter_folder = rel_path.parts[0]

    if str(chapter_folder) not in chapter_list:
        raise Exception(f"file {path} has folder not in chapter list")

    path_no_chapter = Path().joinpath(*rel_path.parts[1:])

    # print(path_no_chapter)

    current_mod_sprite_key = get_key_from_filename(path_no_chapter)

    if current_mod_sprite_key not in mapped_sprites_dict:
        raise Exception(f"Missing mapped sprite for key {current_mod_sprite_key}")

    mapped_sprite = mapped_sprites_dict[current_mod_sprite_key]

    copy_list.append((path, mapped_sprite.full_path))

# for (current_path, mapped_path) in copy_list:
#     print(f"{current_path} -> {mapped_path}")

# print(f"Got {len(copy_list)} items to copy")

trimmed_copy_list = []

unique_keys_this_chapter = {}
current_chapter = None
for (current_path, mapped_path) in copy_list:
    chapter = current_path.parts[1]

    if current_chapter != chapter:
        current_chapter = chapter
        print(f"Begin chapter {chapter}")
        unique_keys_this_chapter.clear()

    path_no_chapter = Path().joinpath(*current_path.parts[2:])
    
    key = get_key_from_filename(path_no_chapter, remove_portrait_sprite_folder=False)

    if key in unique_keys_this_chapter:
        print(f"Will skip duplicate key {key} for {current_path}, existing is {unique_keys_this_chapter[key]}")
    else:
        unique_keys_this_chapter[key] = current_path
        trimmed_copy_list.append((current_path, mapped_path))

    # print(path_no_chapter)

for (current_path, mapped_path) in trimmed_copy_list:
    chapter_number_string = str(current_path.parts[1])
    chapter_number = int(chapter_number_string.replace('ch', ''))

    output_subpath = f'HigurashiEp{chapter_number:02}_Data/StreamingAssets/OGSprites'

    # remove the current_mod_sprites from the current path
    relative_current_path = Path().joinpath(*Path(current_path).parts[2:])

    # print(relative_current_path)




    source = mapped_path
    dest = os.path.join(final_output_path, output_subpath, relative_current_path)

    print(f"{source} -> {dest}")
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source, dest)


# Copy only unique sprites to output
# for key, info in unique_sprite_dict.items():
#     source_path = os.path.join(current_mod_sprites_folder_path, info.firstChapter, info.path)
#     dest_path = os.path.join(current_unique_only, info.firstChapter, info.path)

#     # print(f"{source_path} -> {dest_path}")
#     Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
#     shutil.copy(source_path, dest_path)





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