import os
import subprocess
import time

def check_sql(port, code_path, condition):
    """
    send to the docker the code file, the request and the params
    :return:
    """
    print("check sql injection")

    # Build the Docker image
    os.system('docker build -t sqlserver_fixed .')

    # Run the Docker container in the background
    docker_cmd = f'docker run -p {port}:{port} -e FILE="{code_path}" sqlserver_fixed'
    subprocess.Popen(docker_cmd, shell=True)

    # Wait for the server to start up
    # You can replace the sleep with a more robust check, such as waiting for a response from the server
    time.sleep(5)

    # simulate a sql injection
    print("simulate")
    url = f'http://localhost:{port}/input'
    data = "name=talya&pass=' or 1=1;--"

    curl_cmd = ['curl', '-X', 'POST', url, '-d', data]

    process = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    answer = stdout.decode()  # what
    if condition == answer:
        # the sql injection succeeded!
        return "yes"
    # the sql injection didn't succeed!
    return "no"


print(check_sql(1000, "mini_servers/app/sql_server_fixed.py", "logged in successfully!"))