# semantic-notes

## Overview

Use this markup to get both useful HTML pages, and data that's directly useable in Python.

## In more detail

This application will allow the user to take notes and use special
tags to annotate it for formatting (like Markdown) or for search (like
the semantic web). In essence it's a schemaless database. The idea is
to have a way to take notes from online classes that would then be
searchable in better ways than just fulltext search, but this can be
useful for other forms of knowledge (eg. your book collection, class
notes, biology notes, etc).

## Dependencies

* [MarkupSafe](https://pypi.python.org/pypi/MarkupSafe) for safe html templates.
* [typing](http://mypy.readthedocs.io/en/latest/python2.html). Use `mypy --py2 *.py` to typecheck files.

## Current status

Design / early development
