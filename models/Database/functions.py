from pypika import functions, CustomFunction

functions.GroupConcat = CustomFunction("group_concat", ["field"])
