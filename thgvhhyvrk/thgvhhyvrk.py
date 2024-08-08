import os
PROJECT_NAME = os.environ["project_name"]
print(os.popen("Hello Word: " + PROJECT_NAME).read())