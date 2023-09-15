CWD="$(pwd)"

git clone -b "$branch" "$app_url":streamlit

while ps | grep -q "[ ]$$[ ]$"; do
sleep 1
done

cd streamlit
#python3 -m venv demoapp
#source demoapp/bin/activate
pip install -r "$path_to_requirements_file"
FILE_TO_CHECK=/home/user/.local/lib/python3.11/site-packages/chromadb/__init__.py

if test -f "$FILE_TO_CHECK"; then
    read -r firstline<$FILE_TO_CHECK
    if [ "$firstline" != "__import__('pysqlite3')" ]; 
    then
        sed -i "1i __import__('pysqlite3')" $FILE_TO_CHECK
        sed -i "2i import sys" $FILE_TO_CHECK
        sed -i "3i sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')" $FILE_TO_CHECK
    fi
else
    echo "No ChromaDB to fix"
fi
streamlit run "$path_to_requirements_main_file"
