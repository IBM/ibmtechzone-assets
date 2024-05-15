CWD="$(pwd)"

mkdir -p streamlit_app

git clone https://github.ibm.com/Shivam-Patel3/RAG-Playground-v3.git

while ps | grep -q "[ ]$$[ ]$"; do
sleep 1
done

#python3 -m venv demoapp
#source demoapp/bin/activate
pip install -r "requirements.txt"

streamlit run "app.py"
