CWD="$(pwd)"

git clone $app_url

$git_account

$git_access_token

cd $app_name
python3 -m venv demoapp 
source demoapp/bin/activate 
pip install -r $path_to_requirements_file
streamlit run $path_to_requirements_main_file