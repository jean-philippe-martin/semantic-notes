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
* [Pint](http://pint.readthedocs.io/en/0.8.1/) for units and their conversions.
* [typing](http://mypy.readthedocs.io/en/latest/python2.html). Use `mypy --py2 --ignore-missing-imports *.py` to typecheck files.
* [WebApp2](https://webapp2.readthedocs.io/en/latest/) and [Paste](https://pypi.python.org/pypi/Paste) for serving web pages.

To install them all:

```
pip install webapp2 Paste webob typing Pint MarkupSafe
```


## Current status

Design / early development
