import argparse
import subprocess
import bs4
import json
import os

def extractFromIpynb(t):
    with open(os.path.expanduser(t['file'])) as jsonFile:
        nb = json.loads(jsonFile.read())
        for i, cell in enumerate(nb['cells']):
            if i == int(t['cell']):
                return "".join(cell['source'])

def extractFromFile(t):
    first, last = int(t['from_line']), int(t['to_line'])
    with open(os.path.expanduser(t['file'])) as sourceFile:
        return "".join(
            (line for i,line in enumerate(sourceFile, 1)
             if first <= i <= last))

TEMPLATE = '\n[code language="{0}"]\n{1}\n[/code]\n'

def extractCode(t):
    code = {'nbcell': extractFromIpynb,
            'source': extractFromFile}[t['kind']](t)
    return TEMPLATE.format(t['language'], code)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown_file",
                        help="The input file, in markdown.")
    args = parser.parse_args()
    pandoc_output = subprocess.check_output(
        ["pandoc", "-t", "html", args.markdown_file])
    html = bs4.BeautifulSoup(pandoc_output, "html.parser")
    for r in html.find_all('insert'):
        r.append(extractCode(r))
        r.unwrap()
    print html
    
