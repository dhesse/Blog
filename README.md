# Blog Posts

Pandoc command to convert to HTML

    pandoc -t json 2016-09-26.md|python wpmath.py | pandoc -t html+tex_math_dollars -f json | pbcopy

