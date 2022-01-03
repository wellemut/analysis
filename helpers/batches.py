# Return a list in batches of the given size
# See: https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def batches(list, size):
    for i in range(0, len(list), size):
        yield list[i : i + size]
