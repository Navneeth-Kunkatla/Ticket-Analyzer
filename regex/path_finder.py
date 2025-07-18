import os

def get_file_paths_dict(root_directory):
    file_paths_dict = {}
    for foldername, subfolders, filenames in os.walk(root_directory):
        for filename in filenames:
            full_path = os.path.join(foldername, filename)
            file_paths_dict[filename] = full_path
    return file_paths_dict
