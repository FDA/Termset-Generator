@REM Change /tmp to the path to your directory with CSV files to annotate
@REM Must be an absolute path
@REM For Windows use this syntax: -v "/c/Folder1/Folder2":/data
docker run -d -p 8501:8501 -v "/c/windows/temp":/data termset_generation
