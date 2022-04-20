# super_replace
A script to replace substring in files, including file and folder names, recursively.

1. If the file is binary, only the string in file name is replaced.

2. When doing replacements, the case of the text it replaces is preserved.

   For example, if we want to replace `"abc"` to `"cde"`,
       and if the text is `"abc Abc ABc ABC"`,
   it will be replaced to `"cde Cde CDe CDE"`.

# usage

```
usage: super_replace.py [-h] [--simple-replace] [--replace-in-name-only] [--replace-in-file-only] old new path [path ...]

Replace string in files, including file and folder names, recursively

positional arguments:
  old                   the string to replace
  new                   the replacement string
  path                  the path to the file or folder to replace

optional arguments:
  -h, --help            show this help message and exit
  --simple-replace      simple replacement, aka, not preserve case
  --replace-in-name-only
                        only do the replacement in file or folder names
  --replace-in-file-only
                        only do the replacement in file content
```
