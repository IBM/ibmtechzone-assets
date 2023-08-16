CWD="$(pwd)"

git config --global credential.helper 'store --file ~/.git-credentials'
echo -e "https://github.ibm.com/$git_account:$git_access_token\n" > ~/.git-credentials

git clone $app_url

while ps | grep -q "[ ]$$[ ]$"; do
sleep 1
done

cd $app_name
python3 -m venv demoapp
source demoapp/bin/activate
pip install -r $path_to_requirements_file
streamlit run $path_to_requirements_main_file