import os

def check_create_folder(folder_path):
	"""
	Checks if a folder exists,  and creates it if not.
	:param folder_path: Path to the folder
	"""
	if os.path.exists(folder_path):
		print(f"Folder '{folder_path}' already exists")
		return 0
	else:
		print(f"Folder '{folder_path}' does not exist. Creating it...")
		try:
			os.makedirs(folder_path)
			print(f"Folder '{folder_path}' created successfully.")
		except OSError as e:
			print(f"Error creating folder '{folder_path}': {e}")
			return -1
		return 0
	

def delete_folder(folder_path):
	if os.path.exists(folder_path):
		print(f"Folder '{folder_path}' already exists. Deleting it...")
		try:
			for root, dirs, files in os.walk(folder_path):
				for file in files:
					os.remove(os.path.join(root, file))
				
			os.rmdir(folder_path)
			print(f"Folder '{folder_path}' deleted successfully.")
		except OSError as e:
			print(f"Error deleting folder '{folder_path}': {e}")
			return -1	
		return 0
	else:
		return -1