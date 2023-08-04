#!/bin/bash
mkdir data
cd data
CWD="$(pwd)"
wget ${WGET_URL}
for file in "$CWD"; do
      if [ -d $file ]
      then
              # do something directory-ish
      else
              if [ "$file" == "*.zip" ]       #  this is the snag
              then
                     # do something txt-ish
                     unzip $file
              fi
      fi
done;
