CWD="$(pwd)"

git clone -b "$branch" "$app_url"

while ps | grep -q "[ ]$$[ ]$"; do
sleep 1
done

cd "$app_name"
#python3 -m venv demoapp
#source demoapp/bin/activate
sed -i "1i __import__('pysqlite3')" /home/user/.local/lib/python3.11/site-packages/chromadb/__init__.py
sed -i “2i import sys" /home/user/.local/lib/python3.11/site-packages/chromadb/__init__.py
sed -i “3i sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')" /home/user/.local/lib/python3.11/site-packages/chromadb/__init__.py
pip install -r "$path_to_requirements_file"
streamlit run "$path_to_requirements_main_file"
