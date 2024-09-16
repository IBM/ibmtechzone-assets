import json
import subprocess
import os
import tempfile
import sys
import re
from ibm_botocore.client import Config
import ibm_boto3
import git

def install_dependencies():
    print("### Installing required Python packages...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'gitpython', 'ibm-cos-sdk'], check=True)

def analyze_file_with_cppcheck(file_name):
    cppcheck_executable = '/projects/allScripts/cppcheck-2.11/cppcheck'
    print(f"### Analyzing entire file {file_name} with cppcheck...")
    result = subprocess.run(
        [cppcheck_executable, '--enable=all', '--inconclusive', '--std=c++11', '--language=c++', file_name],
        capture_output=True, text=True
    )

    if result.returncode != 0 or result.stderr:
        return f"cppcheck errors/warnings: {result.stderr}"

    return result.stdout if result.stdout else "No issues found by cppcheck."

def parse_cppcheck_output(output):
    issues = []
    pattern = re.compile(r'(.+?):(\d+):(\d+): (.+?): (.+?) \[(.+?)\]')
    
    for line in output.split('\n'):
        match = pattern.match(line)
        if match:
            file, line_num, col_num, severity, message, checker = match.groups()
            if severity.strip() != 'information':
                issues.append({
                    'file': file.strip(),
                    'line': int(line_num),
                    'column': int(col_num),
                    'severity': severity.strip(),
                    'message': message.strip(),
                    'checker': checker.strip()
                })
    return issues

def read_cpp_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def clone_and_analyze_repo(git_url):
    output = []
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"### Cloning repository {git_url} into {temp_dir}...")
        try:
            repo = git.Repo.clone_from(git_url, temp_dir)
        except git.GitCommandError as e:
            return f"Error cloning repository: {e}"

        cpp_files = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(('.cpp', '.cc', '.cxx', '.h', '.hpp')):
                    relative_path = os.path.relpath(os.path.join(root, file), temp_dir)
                    cpp_files.append((os.path.join(root, file), relative_path))

        if not cpp_files:
            return "No C++ files found in the repository."

        for temp_file, original_file in cpp_files:
            cppcheck_output = analyze_file_with_cppcheck(temp_file)
            parsed_issues = parse_cppcheck_output(cppcheck_output)
            error_issues = [issue for issue in parsed_issues if issue['severity'] == 'error']
            file_content = read_cpp_file(temp_file)
            
            for issue in error_issues:
                issue['file'] = original_file
            output.append({
                'file_name': original_file,
                'file_content': file_content,
                'cppcheck_output': error_issues
            })

    return output

def upload_to_ibm_cloud(data, file_name):
    cos_client = ibm_boto3.client(
        service_name='s3',
        ibm_api_key_id="",
        ibm_service_instance_id="",
        config=Config(signature_version='oauth'),
        endpoint_url=""
    )

    cos_client.put_object(
        Bucket="",
        Key=file_name,
        Body=data
    )

def save_to_local_file(data, file_name):
    with open(file_name, 'w') as file:
        file.write(data)
    print(f"### Analysis results saved to local file: {file_name}")

def main(git_url, upload_to_cloud=False):
    install_dependencies()
    analysis_results = clone_and_analyze_repo(git_url)

    analysis_results_json = json.dumps(analysis_results, indent=2)
    print("### Analysis Results JSON:", analysis_results_json)

    file_name = 'cppcheck_analysis_results_asset.json'

    if upload_to_cloud:
        upload_to_ibm_cloud(analysis_results_json, file_name)
    else:
        save_to_local_file(analysis_results_json, file_name)

if __name__ == "__main__":
    git_url = 'https://github.com/Ohjurot/C-Cpp-Tutorial'  
    # Set upload_to_cloud to True if you want to upload the results, or False if not
    main(git_url, upload_to_cloud=False)
