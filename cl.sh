#!/usr/bin/env bash
find . -name \*.md | xargs grep -h '^\[.*\]: ' | sort | uniq
