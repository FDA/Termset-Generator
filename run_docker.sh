# Change /tmp to the path to your directory with CSV files to annotate
# Must be an absolute path
# For Windows use this syntax: -v "/c/Folder1/Folder2":/data
docker run -d -p 8501:8501 -v /tmp:/data termset_generation
