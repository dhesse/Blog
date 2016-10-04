import argparse
import subprocess
import bs4
import json
import os
import re
from collections import defaultdict

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

def insertFile(t):
    if t.has_attr('lines'):
        first, last = (int(i) for i in t['lines'].split('-'))
    else:
        first, last = 1, float('inf')
    with open(absPath(t['file'])) as sourceFile:
        return "".join(
            (line for i,line in enumerate(sourceFile, 1)
             if first <= i <= last)).strip()

@wordPressCode
def extractFromFile(t):
    return insertFile(t)
    
def insertGist(t):
    return "\nhttps://gist.github.com/{0}/{1}\n".format(
        t['user'], t['id'])

def extractCode(t):
    code = {'nbcell': extractFromIpynb,
            'source': extractFromFile,
            'paste': insertFile,
            'gist': insertGist}[t['kind']](t)
    return code

def detectLanguage(tag):
    if (not tag.has_attr('language')) and tag.has_attr('file'):
        extension = os.path.splitext(tag['file'])[1]
        tag['language'] = defaultdict(
            lambda : "",
            {'.py': 'python',
             '.sh': 'bash',
             '.R': 'r',
             '.html': 'html',
             '.htm': 'html',
             '.js': 'js',
             '.scala': 'scala',
             '.ipynb': 'python'})[extension]

class ReSub(object):
    def __init__(self, seek_pattern, match_list):
        self.seek_pattern = seek_pattern
        self.match_gen = (i for i in match_list)
    def _insert(self, _):
        return self.match_gen.next()
    def __call__(self, text):
        return re.sub(self.seek_pattern, self._insert, text)
        
class HandleLaTeX(object):
    def __init__(self):
        self.latex_groups = []
        self.pattern = "insertLatex"
    def _remember(self, match):
        self.latex_groups.append(
            re.sub("^\$", "$latex ", match.group(0)))
        return self.pattern
    def __call__(self, text):
        return re.sub("(\$.*?\$)", self._remember, text)
    def get_post(self):
        return ReSub(self.pattern, self.latex_groups)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown_file",
                        help="The input file, in markdown.")
    parser.add_argument("-p", "--source_path",
                        default="",
                        help="The path for source code.")
    args = parser.parse_args()
    CONFIG['source_path'] = args.source_path
    with open(args.markdown_file) as input_file:
        input_file_contents = input_file.read()
        pre_filters = [HandleLaTeX()]
        for f in pre_filters:
            input_file_contents = f(input_file_contents)
        post_filters = [f.get_post() for f in pre_filters]
        pandoc_output = subprocess.Popen(
            ["pandoc", "-t", "html"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE).communicate(input=input_file_contents)[0]
        html = bs4.BeautifulSoup(pandoc_output, "html.parser")
        formatargs = []
        for i, r in enumerate(html.find_all('insert')):
            detectLanguage(r)
            r.string = "{{{0}}}".format(i)
            formatargs.append(extractCode(r))
            r.unwrap()
        result = unicode(html).format(*formatargs)
        for f in post_filters:
            result = f(result)
        print result
    
