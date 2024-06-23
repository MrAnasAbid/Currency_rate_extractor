import os
import paramiko

def load_env_variables():
    """
    Load environment variables from the .env file.

    Returns:
    - api_key (str): The API key for the exchange rate API.
    - ssh_host (str): The hostname or IP address of the remote server.
    - ssh_port (int): The port number for SSH connection.
    - ssh_user (str): The username for SSH authentication.
    - ssh_key (str): The path to the private SSH key file for authentication.
    - remote_db_path (str): The file path to the SQLite database on the remote server.
    - remote_ssh_key (str): The path to the public SSH key file for authentication.
    - private_remote_key (str): The path to the private SSH key file for authentication.
    - verbose (bool): Whether to print detailed information.
    """
    api_key = os.getenv('EXCHANGE_RATE_API_KEY', None)
    ssh_host = os.getenv('SSH_HOST', None)
    ssh_port = int(os.getenv('SSH_PORT', 22))  # default to port 22 if not set
    ssh_user = os.getenv('SSH_USER', None)
    local_ssh_key = os.getenv('SSH_KEY_LOCAL_PATH', None)
    remote_ssh_key = os.getenv('SSH_KEY_REMOTE_PATH', None)
    private_remote_key = os.getenv('PRIVATE_KEY_PATH', None)
    remote_db_path = os.getenv('REMOTE_DB_PATH', None)
    verbose = os.getenv('VERBOSE', False)
    return api_key, ssh_host, ssh_port, ssh_user, local_ssh_key, remote_ssh_key, private_remote_key, remote_db_path, verbose

class SQLiteConnection:
    def __init__(self, ssh_host, ssh_port, ssh_user, ssh_key, remote_db_path):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_key = ssh_key
        self.remote_db_path = remote_db_path
    
    def execute_sqlite_commands_on_remote(self, sql_commands, verbose=False):
        """
        Connects to a remote server via SSH and executes SQLite commands on a specified database.

        Args:
        - sql_commands (str or list): The SQL commands to be executed on the SQLite database.
        - verbose (bool): Whether to print detailed information.

        Returns:
        - stdout (str): The standard output from the executed commands.
        - stderr (str): The standard error from the executed commands.
        """
        if isinstance(sql_commands, str):
            sql_commands = [sql_commands]

        if verbose:
            print(f"Executing commands on {self.ssh_host}:{self.ssh_port} as {self.ssh_user}...")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to the remote server
            ssh.connect(self.ssh_host, port=self.ssh_port, username=self.ssh_user, key_filename=self.ssh_key)

            # Run a command to check the shell
            stdin, stdout, stderr = ssh.exec_command("echo $SHELL")
            shell = stdout.read().decode().strip()
            if verbose:
                print(f"Remote shell: {shell}")

            # Prepare the SQLite commands
            commands = "; ".join(sql_commands)
            command = f'sqlite3 {self.remote_db_path} "{commands}"'

            if verbose:
                print(f"Executing command: {command}")

            # Execute the SQLite commands on the remote server
            stdin, stdout, stderr = ssh.exec_command(command)

            # Read the output and error
            stdout_str = stdout.read().decode()
            stderr_str = stderr.read().decode()

            if verbose:
                print("STDOUT:", stdout_str)
                print("STDERR:", stderr_str)

            return stdout_str, stderr_str

        except Exception as e:
            print(f"An error occurred: {e}")
            return "", str(e)

        finally:
            ssh.close()