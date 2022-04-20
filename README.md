# superreplace
A script to replace substring in files, including file and folder names, recursively.

1. If the file is binary, only the string in file name is replaced.

2. When doing replacements, the case of the text it replaces is preserved.

   For example, if we want to replace `"abc"` to `"cde"`,
       and if the text is `"abc Abc ABc ABC"`,
   it will be replaced to `"cde Cde CDe CDE"`.
