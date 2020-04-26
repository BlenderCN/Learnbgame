def parse(lines, descriptions):
    """
    Used to parse ascii files containing a number of different lines

    Possible description params:
    i ... integer
    f ... float
    c ... character
    s ... string
    + ... 1 or more (consumes entire line) TODO what about comments?
    The line will be consumed when the first fitting profile is found,
    so put the most complex requirement for your line FIRST if you have a starting word multiple times

    :param lines: Input lines from lvl file
    :param descriptions: The descriptions in the format [['First word','parser variables'],...]
    :return: A dict containing all the found elements (always arrays)
    """
    # TODO does startswith with an empty string always return true?
    result = {}
    for description in descriptions:  # Fill dict with empty arrays for all entries
        result[description[0]] = []

    for line in lines:
        words = line.split()
        for description in descriptions:
            try:
                result[description[0]].append(parse_line(words, description[0], description[1]))
                break
            except ValueError:
                pass
    return result


def parse_line(words, search_word, description, comment_marker='#'):
    line_result = []
    if len(words) >= len(description)+1 and (words[0] == search_word):  # A valid entry was found
        # Check the rest of the variables
        for i in range(0, len(description)):
            if description[i] == 'i':
                line_result.append(int(words[i+1]))
            elif description[i] == 'f':
                try:
                    line_result.append(float(words[i+1]))
                except ValueError:
                    line_result.append(float(int(words[i+1])))
            elif description[i] == 'c':
                if len(words[i+1]) != 1 or words[i+1].startswith(comment_marker):
                    raise ValueError
                line_result.append(words[i+1])
            elif description[i] == 's':
                if words[i+1].startswith(comment_marker):
                    raise ValueError
                line_result.append(words[i+1])
            elif description[i] == '+':
                line_result.append(words[i+1:len(words)])
                #TODO only add upto the first occurence of comment_marker
    else:
        raise ValueError
    return line_result