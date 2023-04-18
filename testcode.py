import zipfile

zip_file_path = r"C:/Users/LENOVO USER/Desktop/mini_servers.zip"
file_name_to_check = "mini_servers/app/sql_server.py"

with zipfile.ZipFile(zip_file_path, "r") as my_zip:
    print(my_zip.infolist())
    for file_info in my_zip.infolist():
        if file_info.filename == file_name_to_check:
            print(f"{file_name_to_check} exists in the zip file.")
            break

        print(f"{file_name_to_check} does not exist in the zip file.")