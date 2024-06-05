# lyricizer
Automatically match .lrc filenames to song filenames and more

## About
Lyricizer is a Python script that helps you rename your song and lyric files to match each other. Lots of programs require that lyric files have the exact same name as the music file in order to display them together. It uses a similarity threshold to match song files with their corresponding lyric files and proposes a new name for them. The script also allows you to clean up the filename of the song file. This is useful when using 3rd party ripping tools that insert song/album ID or Explicit ratings at the end of the filename. This is most helpful when downloading the .lrc files from another tool from the one you used to obtain your music from, leaving discrepancies between file-naming schemes.

## Features
Cleans up song filenames by removing trailing spaces, hyphens, underscores, dots, and other punctuation.
Finds the artist name from a list of song files for better comparison.
Compares song filenames to lyric filenames and proposes new names based on similarity.
Allows you to set a similarity threshold and the number of attempts to keep adjusting the threshold.
Supports automatic renaming without a confirmation prompt.
Supports different lyric file extensions.

## Usage
The script can be run from the command line, and can be fine-tuned to your purpose through arguments passed along with it:
`python lyricizer.py -s 0.71 -a 5 -l .lrc -r -d /path/to/your/directory -p -t`
Here's what each option does:
```
-s, --similarity_threshold: Set the similarity threshold (default is 0.71).
-a, --attempts: Set the number of attempts to keep lowering the threshold (default is 5).
-l, --lyric_file_extension: Set the lyric file extension (default is .lrc).
-r, --auto_rename: Enable auto renaming without confirmation prompt.
-d, --directory: Set the directory to work in (default is the current working directory).
-p, --keep_punctuation: Don't remove punctuation from song filenames (default is to remove punctuation).
-t, --keep_tagging: Don't remove explicit ratings / ripping artefacts from song filenames (default is to remove tagging).
```
### Basic Usage:
- Run the script using default parameters (no arguments)
- If you are happy with the renames, type `y` into the console to rename all items
- If not, adjust the similarity threshold:
- If not all lyrics files are shown/matched, lower the threshold by typing `l` into the console
- If lyric files are being mis-renamed (usually happens when some songs don't have lyric files associated with them), then increase the threshold by typing `i` into the console
- You should usually get satisfactory results within 2 adjustments

## Dependancies
- os
- re
- difflib
- string
- argparse

## Screenshot
![image](https://github.com/CyberPixel44/lyricizer/assets/37630423/b00ef162-e121-4723-afd0-abdb53af4df4)
