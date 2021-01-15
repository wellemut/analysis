# Get the context from a string surrounding a start and end position, with
# approximately X characters of context to the left and to the right of start.
# The context will expand to avoid terminating in the middle of a word.
def get_context(string, start, end, context):
    # Identify the desired start and end positions
    desired_start_pos = max(start - context, 0)
    desired_end_pos = min(end + context, len(string))

    # Identify the next word break around the desired start and end positions
    start_pos = 0
    end_pos = len(string)
    for word_break in [" ", "\n"]:
        # Identify the word break before the desired_start_pos
        start_break_pos = string.rfind(word_break, 0, desired_start_pos)
        if start_break_pos > start_pos and start_break_pos != -1:
            start_pos = start_break_pos

        # Identify the word breakd after the desired_end_pos
        end_break_pos = string.find(word_break, desired_end_pos)
        if end_break_pos < end_pos and end_break_pos != -1:
            end_pos = end_break_pos

    return string[start_pos:end_pos].strip()
