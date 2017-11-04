#!/bin/bash
set -e

for x in test*.py; do
  python $x
done

# mypy can't find pint from the virtualenv, but that's OK,
# we're not typechecking pint itself.
mypy --py2 --ignore-missing-imports *.py && echo "Typecheck OK"
