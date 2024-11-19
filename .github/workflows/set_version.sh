#!/bin/sh

version_string=$(git rev-parse HEAD | head -c 8)
version_string=$(echo "ibase=16; $(echo "$version_string" | tr 'a-z' 'A-Z')" | bc)

sed -i "s|version = \"\([0-9]*\).\([0-9]*\).\([0-9]*\).dev\([0-9]*\)\"|version = \"\1\.\2\.\3.dev$version_string\"|g" $1
