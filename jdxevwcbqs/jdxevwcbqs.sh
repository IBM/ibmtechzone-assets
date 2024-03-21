#!/bin/bash

wwpn="$1"

if [[ $wwpn == *":"* ]]; then
    new_wwpn=$(echo "$wwpn" | sed 's/://g')
else
    new_wwpn=$(echo "$wwpn" | sed 's/../&:/g; s/:$//')
fi

echo "$new_wwpn"