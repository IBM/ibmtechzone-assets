#!/bin/bash
mkdir -p data
cd data
CWD="$(pwd)"
wget $wget_url
for f in "$CWD"/*
do
    if [ -f *.zip ]; 
    then
        unzip $f
    fi
done