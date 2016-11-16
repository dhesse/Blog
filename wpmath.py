from pandocfilters import toJSONFilter, Str, RawBlock
import re
from itertools import islice

def getLines(attrs):
    lines_re = re.match("(\d+)-(\d+)", attrs.get('lines', ""))
    if lines_re:
        return (int(lines_re.group(1)),
                int(lines_re.group(2)) + 1)
    return (0, None)

def wpmath(key, value, format, meta):
    if key == "Math":
        return Str("$LaTeX " + value[1] + "$")
    if key == "CodeBlock":
        language = value[0][1]
        attrs = dict(value[0][2])
        if 'fromFile' in attrs:
            with open(attrs['fromFile']) as codeFile:
                return RawBlock(value[0], '\n'.join(islice(codeFile, *getLines(attrs))))
        #print value
        #return RawBlock(value[0], str(value[1]))

if __name__ == "__main__":
    toJSONFilter(wpmath)
