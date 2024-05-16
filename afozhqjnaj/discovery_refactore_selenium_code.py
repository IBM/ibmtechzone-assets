import os
import re

def categorize_selenium_java_file(file_path):
    """
    Categorize a Selenium Java file into "Object File", "Test Case File", or "Other".
    
    Args:
        file_path (str): Path to the Selenium Java file.
        
    Returns:
        str: Category of the file ("Object File", "Test Case File", or "Other").
    """
    # Define regex patterns to identify relevant keywords
    test_import_keywords = [
        "org.junit.",
        "junit.",
        "org.junit"
    ]
    
    object_import_keywords = [
        "org.openqa.selenium.",
        "org.openqa.selenium.support."
    ]
    object_pattern = r'class\s+(\w+)Page\s*\{'
    test_pattern = r'@Test'
    
    
    content = ''
    # Open the Java file and read its contents
    try:
        with open(file_path, encoding='utf-8') as file:
            #content = file.read()
            lines = file.readlines()
            content = "\n".join(lines)
    except:
        with open(file_path, encoding='latin-1') as file:
            #content = file.read()
            lines = file.readlines()
            content = "\n".join(lines)
    test_import_count = 0
    object_import_count = 0
    # Count relevant import statements
    # if "CheckoutPage.java" in file_path:
    #     print(lines,"\n")
    import_lib_list = []
    for line in lines:
        if line.strip().startswith("import"):
            # if "CheckoutPage.java" in file_path:
                # print(line,"\n")
            line = line.strip().replace("import", "").replace(";", "")
            if line:
                import_lib_list.append(line.strip().split('.')[-1])
            
            # Check for test-related imports
            if any(keyword in line for keyword in test_import_keywords):
                test_import_count += 1
            
            # Check for object-related imports
            if any(keyword in line for keyword in object_import_keywords):
                object_import_count += 1          
    #print("Files:",file_path,test_import_count,object_import_count)
    # Check for patterns to determine the category
    if re.search(object_pattern, content) or (test_import_count == 0 and object_import_count > 0):
        return "Object File",import_lib_list
    elif re.search(test_pattern, content) or (test_import_count > 0 and object_import_count == 0):
        return "Test Case File",import_lib_list
    elif test_import_count > 0 and object_import_count > 0:
        return "both",import_lib_list
    else:
        return "Other",import_lib_list
        
def find_selenium_files(folder_path):
    test_files = []
    object_files = []
    file_import_lib_dict = {}

    # Define regex patterns for matching test and object files
    test_file_pattern = r'.*Test\.java$'
    object_file_pattern = r'.*Page\.java$'

    # Iterate over all files in the specified folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            category_class,import_lib_list = categorize_selenium_java_file(file_path)
            if "java" in file_path[-5:]:
                file_import_lib_dict[file_path] = import_lib_list
            # Check if the file is a Selenium test file
            if re.match(test_file_pattern, file):
                test_files.append(file_path)
            # Check if the file is a Selenium object file
            elif re.match(object_file_pattern, file):
                object_files.append(file_path)
            else:
                if file_path[-5:]!=".java":
                    continue
                if category_class=="Object File":
                    object_files.append(file_path)
                elif category_class=="Test Case File":
                    test_files.append(file_path)
                elif category_class=="both":
                    test_files.append(file_path)

    return test_files, object_files,file_import_lib_dict



def code_discovery_and_refactore(folder_path):
    # Call the function to find Selenium test and object files
    test_files, object_files,file_import_lib_dict = find_selenium_files(folder_path)

    # Print the paths of Selenium test files
    import_name_to_file_dict = {}
    print("Selenium Test Files:")
    for file_path in test_files:
        print(file_path)
        import_name_to_file_dict[file_path.split('/')[-1][:-5]] = file_path

    # Print the paths of Selenium object files
    print("\nSelenium Object Files:")
    for file_path in object_files:
        print(file_path)
        import_name_to_file_dict[file_path.split('/')[-1][:-5]] = file_path

    test_files_with_dependency = {}
    for file_path in test_files:
        library_list = file_import_lib_dict.get(file_path,[])
        dependency_files = [import_name_to_file_dict[lib] for lib in library_list if import_name_to_file_dict.get(lib,'')]
        test_files_with_dependency[file_path] = dependency_files

    # print main and dependency files
    # for key_path in test_files_with_dependency:
    #     print("Main File:",key_path)
    #     print("Dependent File: \n")
    #     for dep_file in test_files_with_dependency[key_path]:
    #         print(dep_file)
        
    return test_files_with_dependency
            
            