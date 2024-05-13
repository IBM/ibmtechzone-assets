import os
def get_all_files_in_directory(directory_path):
    file_list = []
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list

# Provide the path to the directory---"DO NOT USE "." before the extension, for example use txt instead of .txt"
def file_mapping(path, extension):

    # Get the list of all files in the directory and subdirectories
    files = get_all_files_in_directory(path)

    # Extract file names and extensions using os.path.splitext
    file_dict = {os.path.splitext(file)[0]: os.path.splitext(file)[1][1:] for file in files}
    desired_extension = extension
    # Filter files based on the desired extension (case-insensitive)
    filtered_files = {filename: extension for filename, extension in file_dict.items() if extension.lower() == desired_extension.lower()}
    md_file_path = dict(zip(filtered_files.keys(), [os.path.basename(file) for file in filtered_files]))
    return md_file_path, print(f"There are a total of {len(list(filtered_files.keys()))} files in the data provided by the client.")