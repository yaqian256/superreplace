"""
A script to replace substring in files, including file and folder names, recursively.

1. If the file is binary, only the string in file name is replaced.

2. When doing replacements, the case of the text it replaces is preserved.

   For example, if we want to replace "abc" to "cde",
       and if the text is "abc Abc ABc ABC",
   it will be replaced to "cde Cde CDe CDE".
"""
import os
import argparse
import subprocess
import re

try:
    import chardet
except ImportError:
    print("chardet is not installed, please install it with `pip install chardet`")
    exit(1)


def is_binary(path):
    assume_text = {
        ".cfg",
        ".conf",
        ".crt",
        ".cs",
        ".css",
        ".html",
        ".ini",
        ".j2",
        ".js",
        ".json",
        ".md",
        ".pem",
        ".ps1",
        ".psm1",
        ".py",
        ".rst",
        ".sh",
        ".txt",
        ".xml",
        ".xsd",
        ".yaml",
        ".yml",
    }

    assume_binary = {
        ".bin",
        ".eot",
        ".gz",
        ".ico",
        ".iso",
        ".jpg",
        ".otf",
        ".p12",
        ".png",
        ".pyc",
        ".rpm",
        ".ttf",
        ".woff",
        ".woff2",
        ".zip",
    }

    ext = os.path.splitext(path)[1]

    if ext in assume_text:
        return False

    if ext in assume_binary:
        return True

    with open(path, "rb") as path_fd:
        return b"\0" in path_fd.read(4096)


def is_from_git_repo(path):
    try:
        if os.path.isfile(path):
            path = os.path.dirname(path)
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"], cwd=path)
        return True
    except subprocess.CalledProcessError:
        return False


def rename_file(old, new, use_git_mv=False):
    if use_git_mv:
        subprocess.call(["git", "mv", "-f", old, new])
    else:
        os.rename(old, new)


def case_sensitive_replace(string, old, new):
    """ replace occurrences of old with new, within string
        replacements will match the case of the text it replaces
    """

    def repl(match):
        current = match.group()
        result = ""
        all_upper = True
        for i, c in enumerate(current):
            if i >= len(new):
                break
            if c.isupper():
                result += new[i].upper()
            else:
                result += new[i].lower()
                all_upper = False
        # append any remaining characters from new
        length = min(len(current), len(new))
        if all_upper:
            result += new[length:].upper()
        else:
            result += new[length:].lower()
        return result

    regex = re.compile(re.escape(old), re.I)
    newstring = regex.sub(repl, string)
    if " " in old:
        regex = re.compile(re.escape(old.replace(" ", "")), re.I)
        new = new.replace(" ", "")
        return regex.sub(repl, newstring)
    return newstring


def string_replace(string, old, new, preserve_case=True):
    """replace string in a single string"""
    if preserve_case:
        return case_sensitive_replace(string, old, new)
    else:
        return string.replace(old, new)


def detect_encoding(file_path):
    try:
        with open(file_path, "rb") as fp:
            return chardet.detect(fp.read())["encoding"]
    except:
        return None


def replace_in_file(old, new, file_path, preserve_case=True):
    """replacea string in a single file"""

    if is_binary(file_path):
        print("skipping binary file: " + file_path)
        return
    print("replacing in file: " + file_path)

    encoding = detect_encoding(file_path)
    if not encoding:
        encoding = "utf-8"

    with open(file_path, "r", encoding=encoding) as fp:
        content = fp.read()
    new_content = string_replace(content, old, new, preserve_case)
    with open(file_path, "w", encoding=encoding) as fp:
        fp.write(new_content)


def remove_empty_folders(path):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_empty_folders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0:
        print("removing empty folder: " + path)
        os.rmdir(path)


def get_files(path):
    if os.path.isfile(path):
        yield path
    for root, _, files in os.walk(path):
        for file in files:
            yield os.path.join(root, file)


def replace_in_file_and_names(old, new, path, in_name, in_file, preserve_case):
    """replace string in files, including file and folder names, recursively"""
    use_git_mv = is_from_git_repo(path)

    for file in get_files(path):
        # The new file name.
        new_file = file
        if in_name:
            new_file = string_replace(file, old, new, preserve_case)
            if new_file != file:
                new_dir = os.path.dirname(new_file)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                rename_file(file, new_file, use_git_mv)
        if in_file:
            replace_in_file(old, new, new_file)
    # remove empty folders after replacing in file and folder names
    if in_name:
        remove_empty_folders(path)


def main():
    parser = argparse.ArgumentParser(
        description="Replace string in files, including file and folder names, recursively"
    )
    parser.add_argument("old", help="the string to replace")
    parser.add_argument("new", help="the replacement string")
    parser.add_argument(
        "path", nargs="+", help="the path to the file or folder to replace"
    )
    parser.add_argument(
        "--simple-replace",
        action="store_true",
        help="simple replacement, aka, not preserve case",
    )
    parser.add_argument(
        "--replace-in-name-only",
        action="store_true",
        help="only do the replacement in file or folder names",
    )
    parser.add_argument(
        "--replace-in-file-only",
        action="store_true",
        help="only do the replacement in file content",
    )

    args = parser.parse_args()

    in_name = in_file = True
    if args.replace_in_name_only:
        in_file = False
    if args.replace_in_file_only:
        in_name = False

    preserve_case = not args.simple_replace
    for path in args.path:
        print("processing " + path)
        replace_in_file_and_names(
            args.old, args.new, path, in_name, in_file, preserve_case
        )


if __name__ == "__main__":
    main()
