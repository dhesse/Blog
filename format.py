import argparse
import subprocess
import bs4
import json
import os

TEMPLATE = '\n[code language="{0}"]\n{1}\n[/code]\n'
CONFIG = {'source_path': ''}

def absPath(filename):
    return os.path.expanduser(
        os.path.join(CONFIG['source_path'], filename))

def extractFromIpynb(t):
    with open(absPath(t['file'])) as jsonFile:
        nb = json.loads(jsonFile.read())
        for i, cell in enumerate(nb['cells']):
            if i == int(t['cell']):
                return "".join(cell['source'])

def extractFromFile(t):
    first, last = (int(i) for i in t['lines'].split('-'))
    with open(absPath(t['file'])) as sourceFile:
        return "".join(
            (line for i,line in enumerate(sourceFile, 1)
             if first <= i <= last)).strip()

def extractCode(t):
    code = {'nbcell': extractFromIpynb,
            'source': extractFromFile}[t['kind']](t)
    return TEMPLATE.format(t['language'], code)

def detectLanguage(tag):
    if 'language' not in tag:
        extension = os.path.splitext(tag['file'])[1]
        tag['language'] = {'.py': 'python',
                           '.ipynb': 'python'}[extension]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown_file",
                        help="The input file, in markdown.")
    parser.add_argument("-p", "--source_path",
                        default="",
                        help="The path for source code.")
    args = parser.parse_args()
    CONFIG['source_path'] = args.source_path
    pandoc_output = subprocess.check_output(
        ["pandoc", "-t", "html", args.markdown_file])
    html = bs4.BeautifulSoup(pandoc_output, "html.parser")
    for r in html.find_all('insert'):
        detectLanguage(r)
        r.append(extractCode(r))
        r.unwrap()
    print html
    
