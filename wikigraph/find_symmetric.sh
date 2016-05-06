#!/bin/sh

# This script finds symmetric links (A -> B and B -> A). It takes two inputs.
# The first is a file with articles and the second is a file to which output
# this feature. The output file WILL(!) BE OVERWRITEN.
#
# Expected form of file with articles:
#
# article1@article2 article1 article2
# article2@article1 article2 article1
# article2@article3 article2 article2
# ...



if [ -e "$2" ]
then
  rm "$2"
fi

while read -r id v1 v2 rest || [ -n "$line" ]; do
  if grep -m 1 -F -e "$v2@$v1" "$1" > /dev/null
  then
    echo "$v1@$v2 1" >> "$2"
  else
    echo "$v1@$v2 -1" >> "$2"
  fi
done < "$1"

