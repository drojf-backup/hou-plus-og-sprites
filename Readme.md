## Folder Descriptions

- fixed_sprites_uncompressed: unoptimized hand edited images
- fixed_sprites: optimized hand edited images
- Higurashi Hou Plus Sprites: optimized versions of the raw images from hou+
- Higurashi Hou Plus Sprites Uncompressed: the raw images from hou+
- out_for_mod_fixed: all the files used in the mod for all chapters, however only the unique values and not all the values

## Workflow

- Iterate through all images in `current_mod_sprites`
- If the image is unecessary (it has the same postfix number as another already copied file IN THE SAME FOLDER), just skip it
- Find the corresponding image in `out_for_mod_fixed` (may need to build a database of filenames for this) 
- Copy to final output
- Note: these images should already be optimized (?), so don't need to optimize them again. 