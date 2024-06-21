import os
import sys
import requests
import pandas as pd
import sqlite3
import paramiko
from pathlib import Path

# ROOT is above the folder this code is in
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
from src.constants import BASE_CURRENCY
from src.utils import load_env_variables

def execute_sqlite_commands_on_remote(ssh_host, ssh_port, ssh_user, ssh_key, remote_db_path, sql_commands, verbose = False):
    """
    Connects to a remote server via SSH and executes SQLite commands on a specified database.

    Args:
    - ssh_host (str): The hostname or IP address of the remote server.
    - ssh_port (int): The port number for SSH connection.
    - ssh_user (str): The username for SSH authentication.
    - ssh_key (str): The path to the private SSH key file for authentication.
    - remote_db_path (str): The file path to the SQLite database on the remote server.
    - sql_commands (str): The SQL commands to be executed on the SQLite database.

    Returns:
    - stdout (str): The standard output from the executed commands.
    - stderr (str): The standard error from the executed commands.
    """
    # Create an SSH client
    if sql_commands is None:
        return None, "No SQL commands provided, exiting..."

    if verbose:
        print(f"ssh_host: {ssh_host}")
        print(f"ssh_port: {ssh_port}")
        print(f"ssh_user: {ssh_user}")
        print(f"ssh_key: {ssh_key}")
        print(f"remote_db_path: {remote_db_path}")
        print(f"sql_commands: {sql_commands}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote server
        ssh.connect(ssh_host, port=ssh_port, username=ssh_user, key_filename=ssh_key)

        # Prepare the SQLite commands and pipe them into sqlite3
        commands = f"echo '{sql_commands}' | sqlite3 {remote_db_path}"
                # Prepare the SQLite command
        if type(sql_commands) == str:
            sql_commands = [sql_commands]
        commands = "; ".join(sql_commands)
        command = f'sqlite3 {remote_db_path} "{commands}"'
        print(command)

        # Execute the SQLite commands on the remote server
        stdin, stdout, stderr = ssh.exec_command(commands)
        return stdout.read().decode(), stderr.read().decode()
    except Exception as e:
        print(f"An error occurred: {e}")
        return "", str(e)
    finally:
        ssh.close()


# Example usage
if __name__ == '__main__':
    api_key, vm_ip, verbose, ssh_host, ssh_port, ssh_user, ssh_key, remote_db_path = load_env_variables()
    
    print(f"API key: {api_key}")
    print(f"VM IP address: {vm_ip}")
    print(f"Verbose: {verbose}")
    print(f"SSH host: {ssh_host}")
    print(f"SSH port: {ssh_port}")
    print(f"SSH user: {ssh_user}")
    print(f"SSH key: {ssh_key}")
    print(f"Remote DB path: {remote_db_path}")
    
    sql_commands = """
    SELECT * FROM users;
    INSERT INTO users (id, name, age) VALUES (4, 'John Doe', '27');
    SELECT * FROM users;
    """
    
    stdout, stderr = execute_sqlite_commands_on_remote(
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_user=ssh_user,
        ssh_key=ssh_key,
        remote_db_path=remote_db_path,
        sql_commands=sql_commands
    )
    
    print("STDOUT:", stdout)
    print("STDERR:", stderr)

