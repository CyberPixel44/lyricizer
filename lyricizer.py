# Python script that tries to match the song filename to the .lrc filename that are close but not exact matches. Also cleans up the original song filename to a standard format.
# Things to remove from original filename: any mix of alphanumerics within square brackets, ex: [as238] or any explicit rating, ex: [E] or [e] only. Wont remove any other square brackets, e: [feat.], [remix], [live], [acoustic], etc.
# Once the original filename is cleaned up, compare it to the .lrc filename and find the closest match.
# Ask for comfirmation before renaming the original song filenames to the cleaned up song filenames by showing the original and cleaned up filenames side by side.
# Steps taken to compare names:
# Find artist name by finding the repeating words in only the song filename and not the .lrc filename.
# Ignore the artist name and compare the rest of the song filename to the .lrc filename.
# If track numbers are present in both filenames, compare them in addition to the rest of the filename.
# Once the comparison is done, ask for confirmation before renaming the files.

import os
import re
import difflib
import argparse

keep_punctuation = True
keep_tagging = True  # Square brackets with explicit ratings, ex: [E] or [e] or any mix of alphanumerics, ex: [as238]


def print_colored_diff(old_name, new_name):
    diff = difflib.ndiff(old_name, new_name)
    result = ''
    for i in diff:
        if i[0] == '-':
            result += f"{Colors.RED}{i[-1]}{Colors.RESET}"
        elif i[0] == '+':
            result += f"{Colors.GREEN}{i[-1]}{Colors.RESET}"
        else:
            result += i[-1]
    return result


class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'


# Function to clean up the song filename
def clean_song_filename(song_filename):
    # Remove any mix of alphanumerics within square brackets
    if keep_tagging:
        song_filename = re.sub(r'\[[a-zA-Z0-9]*\]', '', song_filename)
    # Remove explicit ratings
    if keep_tagging:
        song_filename = re.sub(r'\[E\]|\[e\]', '', song_filename)
    # Remove any extra spaces
    song_filename = re.sub(r'\s{2,}', ' ', song_filename)
    # Remove any leading or trailing spaces
    song_filename = song_filename.strip()
    # Remove any leading or trailing hyphens
    song_filename = song_filename.strip('-')
    # Remove any leading or trailing underscores
    song_filename = song_filename.strip('_')
    # Remove any leading or trailing dots
    song_filename = song_filename.strip('.')
    # Remove any leading or trailing dashes
    song_filename = song_filename.strip('-')
    # Remove any trailing spaces, periods, or other punctuation before the file extension
    if keep_punctuation:
        song_filename = re.sub(r'[\s\.\-_]+(\.[a-zA-Z0-9]+)$', r'\1', song_filename)
    return song_filename


# Function to find the artist name
def find_artist_name(songlist):
    word_map = {}
    for song in songlist:
        words = song.split()
        for word in words:
            if word in word_map:
                word_map[word] += 1
            else:
                word_map[word] = 1
    common_words = {word for word, count in word_map.items() if count == len(songlist)}
    longest_sequence = ''
    for song in songlist:
        words = song.split()
        current_sequence = ''
        for i in range(len(words) - 1):
            if words[i] in common_words and words[i + 1] in common_words:
                current_sequence += ' ' + words[i]
            else:
                if len(current_sequence) > len(longest_sequence):
                    longest_sequence = current_sequence
                current_sequence = ''
        # Check for the last word in the song
        if words[-1] in common_words:
            current_sequence += ' ' + words[-1]
        if len(current_sequence) > len(longest_sequence):
            longest_sequence = current_sequence
    return longest_sequence.strip()


def lyricizer(song_filenames, lrc_filenames, similarity_threshold, attempts, lyric_file_extension, auto_rename,
              directory):
    artist_name = find_artist_name(song_filenames)
    rename_map = {}
    song_rename_map = {}
    attempt_count = 0
    lyric_filecount = len(lrc_filenames)
    while attempt_count < attempts:
        for song_filename in song_filenames:
            cleaned_song_filename = clean_song_filename(song_filename)
            song_rename_map[song_filename] = cleaned_song_filename
            cleaned_song_filename_for_comparison = cleaned_song_filename.replace(artist_name, '')
            max_similarity = 0
            closest_lrc_filename = None
            for lrc_filename in lrc_filenames:
                similarity = difflib.SequenceMatcher(None, cleaned_song_filename_for_comparison, lrc_filename).ratio()
                if similarity > max_similarity:
                    max_similarity = similarity
                    closest_lrc_filename = lrc_filename
            if closest_lrc_filename is not None and max_similarity >= similarity_threshold:
                new_lrc_filename = os.path.splitext(cleaned_song_filename)[0] + lyric_file_extension
                counter = 1
                while os.path.exists(os.path.join(directory, new_lrc_filename)):
                    name, ext = os.path.splitext(cleaned_song_filename)
                    new_lrc_filename = f"{name}({counter}){ext}"
                    counter += 1
                rename_map[closest_lrc_filename] = new_lrc_filename

        print(f"Artist:{Colors.YELLOW}", artist_name, f"{Colors.RESET}")
        print(f"Similarity threshold:{Colors.YELLOW}", round(similarity_threshold, 2), f"{Colors.RESET}\n")

        print("Proposed song renames:")
        for old_name, new_name in song_rename_map.items():
            print(print_colored_diff(old_name, new_name))
        print("\n")

        print("Proposed", lyric_file_extension, "renames:")
        for old_name, new_name in rename_map.items():
            print(print_colored_diff(old_name, new_name))
        print("\n")

        print(f"Total song files:{Colors.YELLOW}", len(song_filenames), f"{Colors.RESET}")
        print(f"Total .lrc files:{Colors.YELLOW}", lyric_filecount, f"{Colors.RESET}")
        print(f"Total proposed renames:{Colors.YELLOW}{len(rename_map)}/{lyric_filecount}{Colors.RESET}")
        print(f"Missed lyric files:{Colors.RED}{lyric_filecount - len(rename_map)}/{lyric_filecount}{Colors.RESET}\n")

        if auto_rename:
            confirm = 'y'
        else:
            confirm = input('Rename all the files (y), increase threshold (i), lower threshold (l) or exit (e): ')
        if confirm.lower() == 'y':
            for old_name, new_name in song_rename_map.items():
                os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
            print(f"{Colors.GREEN}All song files renamed successfully{Colors.RESET}")
            for old_name, new_name in rename_map.items():
                os.rename(os.path.join(directory, old_name), os.path.join(directory, new_name))
            print(f"{Colors.GREEN}All{Colors.CYAN}", lyric_file_extension,
                  f"{Colors.GREEN}files renamed successfully{Colors.RESET}")
            break
        elif confirm.lower() == 'i':
            print(f"{Colors.YELLOW}Files not renamed, increasing match threshold...{Colors.RESET}")
            similarity_threshold += 0.1
            attempt_count += 1
            if attempt_count == attempts:
                print(f"{Colors.RED}Reached maximum number of attempts. Quitting...{Colors.RESET}")
        elif confirm.lower() == 'l':
            print(f"{Colors.RED}Files not renamed, lowering match threshold...{Colors.RESET}")
            similarity_threshold -= 0.1
            attempt_count += 1
            if attempt_count == attempts:
                print(f"{Colors.RED}Reached maximum number of attempts. Quitting...{Colors.RESET}")
        else:
            print(f"{Colors.RED}Exiting...{Colors.RESET}")
            break


def main():
    global keep_punctuation
    global keep_tagging

    parser = argparse.ArgumentParser(description='Lyricizer')
    parser.add_argument('-s', '--similarity_threshold', type=float, default=0.71, help='Similarity threshold [0.1 to 1]')
    parser.add_argument('-a', '--attempts', type=int, default=5, help='Number of attempts to keep lowering the threshold')
    parser.add_argument('-l', '--lyric_file_extension', type=str, default='.lrc', help='Lyric file extension (ex: .lrc)')
    parser.add_argument('-r', '--auto_rename', action='store_true', help='Auto rename without confirmation prompt')
    parser.add_argument('-d', '--directory', type=str, default=os.getcwd(), help='Directory to work in (default: current working directory)')
    parser.add_argument('-p', '--keep_punctuation', action='store_false', default=True,
                        help='Don\'t remove punctuation from song filenames (default: removes punctuation)')
    parser.add_argument('-t', '--keep_tagging', action='store_false', default=True,
                        help='Don\'t remove explicit ratings / ripping artefacts from song filenames (ex: [E], [USL1276]) (default: removes tagging)')

    args = parser.parse_args()

    keep_punctuation = args.keep_punctuation
    keep_tagging = args.keep_tagging

    # Get the current working directory
    cwd = args.directory
    # Get all the files in the current working directory
    files = os.listdir(cwd)
    # Get all the song files
    song_files = [file for file in files if file.endswith(('.mp3', '.m4a', '.wav', '.flac', '.ogg', '.aac', '.wma'))]
    # Get all the .lrc files
    lrc_files = [file for file in files if file.endswith(args.lyric_file_extension)]
    # Compare the song filenames to the .lrc filenames
    lyricizer(song_files, lrc_files, args.similarity_threshold, args.attempts, args.lyric_file_extension,
              args.auto_rename, args.directory)


if __name__ == '__main__':
    main()
