CWD="$(pwd)"
wget $wget_url
for f in "$CWD"/*
do
    if [ -f *.zip ]; 
    then
        unzip $f
    fi
done

cd rag-APP-main
CREATE VIRTUAL ENV
PIP INSTALL -r requiremrnts.txt
streamlist hello