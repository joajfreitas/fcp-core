#!/bin/sh

sed -i "s|version = \"\([0-9]*\).\([0-9]*\).\([0-9]*\)\"|version = \"\1\.\2\.\3+$(git rev-parse HEAD | head -c 8)\"|g" $1
