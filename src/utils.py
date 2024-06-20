import os

def load_env_variables():
    """
    Load environment variables and return them.
    
    Returns:
    - api_key (str): API key for exchange rate service.
    - vm_ip (str): IP address of the VM.
    - verbose (str): Verbose mode flag.
    - ssh_host (str): SSH host address.
    - ssh_port (int): SSH port.
    - ssh_user (str): SSH username.
    - ssh_key (str): Path to SSH private key.
    - remote_db_path (str): Path to the SQLite database on the remote server.
    """
    api_key = os.getenv('EXCHANGE_RATE_API_KEY')
    vm_ip = os.getenv('VM_IP_ADDRESS')
    verbose = os.getenv('VERBOSE')
    ssh_host = os.getenv('SSH_HOST')
    ssh_port = int(os.getenv('SSH_PORT', 22))  # default to port 22 if not set
    ssh_user = os.getenv('SSH_USER')
    ssh_key = os.getenv('SSH_KEY')
    remote_db_path = os.getenv('REMOTE_DB')
    return api_key, vm_ip, verbose, ssh_host, ssh_port, ssh_user, ssh_key, remote_db_path