CWD="$(pwd)"

mkdir -p streamlit_app

git clone -b "$branch" "$streamlit_app_repo" streamlit_app

while ps | grep -q "[ ]$$[ ]$"; do
sleep 1
done

#python3 -m venv demoapp
#source demoapp/bin/activate
pip install -r "streamlit_app/$path_to_requirements_file"
read -r firstline</home/user/.local/lib/python3.11/site-packages/chromadb/__init__.py
if [ "$firstline" != "__import__('pysqlite3')" ]; 
then
    sed -i "1i __import__('pysqlite3')" /home/user/.local/lib/python3.11/site-packages/chromadb/__init__.py
    sed -i "2i import sys" /home/user/.local/lib/python3.11/site-packages/chromadb/__init__.py
    sed -i "3i sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')" /home/user/.local/lib/python3.11/site-packages/chromadb/__init__.py
fi
streamlit run "streamlit_app/$path_to_streamlit_file"
