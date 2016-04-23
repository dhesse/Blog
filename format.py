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

def wordPressCode(fmt):
    def wpFmt(tag):
        return TEMPLATE.format(
            tag['language'],
            fmt(tag))
    return wpFmt

@wordPressCode
def extractFromIpynb(t):
    with open(absPath(t['file'])) as jsonFile:
        nb = json.loads(jsonFile.read())
        for i, cell in enumerate(nb['cells']):
            if i == int(t['cell']):
                return "".join(cell['source'])

@wordPressCode
def extractFromFile(t):
    first, last = (int(i) for i in t['lines'].split('-'))
    with open(absPath(t['file'])) as sourceFile:
        return "".join(
            (line for i,line in enumerate(sourceFile, 1)
             if first <= i <= last)).strip()

def insertGist(t):
    return "\nhttps://gist.github.com/{0}/{1}\n".format(
        t['user'], t['id'])

def extractCode(t):
    code = {'nbcell': extractFromIpynb,
            'source': extractFromFile,
            'gist': insertGist}[t['kind']](t)
    return code

def detectLanguage(tag):
    if (not tag.has_attr('language')) and tag.has_attr('file'):
        extension = os.path.splitext(tag['file'])[1]
        tag['language'] = {'.py': 'python',
                           '.R': 'r',
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
    
