# Batch list elements into groups of n
# in_batches([1, 2, 3, 4, 5]) -> [[1, 2], [3, 4], [5]]
# From: https://stackoverflow.com/a/312464/6451879
def in_batches(list, n=1):
    l = len(list)
    for ndx in range(0, l, n):
        yield list[ndx : min(ndx + n, l)]
