#!/bin/bash
set -e

for x in test*.py; do
  python $x
done

mypy --py2 *.py && echo "Typecheck OK"
