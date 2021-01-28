import filetype

# Return true if the string is of binary type (e.g., PDF)
def is_binary_string(string):
    return filetype.guess(string) is not None
