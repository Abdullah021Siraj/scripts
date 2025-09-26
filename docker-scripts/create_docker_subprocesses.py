import subprocess
import sys

CONTAINER_NAME = "your-container-name"
IMAGE_NAME = "container-name:tag"
HOST_PORT = desired port
CONTAINER_PORT = desired port

def log(message):
    print(f"[{CONTAINER_NAME} Automation] {message}")

def container_is_running():
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name={CONTAINER_NAME}', '--quiet'],
            capture_output=True,
            text=True,
            check=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        log(f"Error checking container status: {e}")
        return False

def start_or_create_container():
    try:
        log(f"Attempting to start existing container '{CONTAINER_NAME}'...")
        subprocess.run(
            ['docker', 'start', CONTAINER_NAME],
            check=True,
            capture_output=True
        )
        log(f"Container '{CONTAINER_NAME}' started successfully.")
    except subprocess.CalledProcessError:
        log(f"Container '{CONTAINER_NAME}' not found. Creating a new one...")
        try:
            subprocess.run(
                ['docker', 'run', '-d', '-p', f'{HOST_PORT}:{CONTAINER_PORT}', 
                 '--name', CONTAINER_NAME, IMAGE_NAME],
                check=True,
                capture_output=True
            )
            log(f"New container '{CONTAINER_NAME}' created and started from image '{IMAGE_NAME}'.")
        except subprocess.CalledProcessError as e:
            log(f"Failed to create new container: {e.stderr.strip()}")
            sys.exit(1)

def perform_health_check():
    log("Performing HTTP health check...")
    try:
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
             f'http://localhost:{HOST_PORT}'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        http_code = result.stdout.strip()
        if http_code == "200":
            log(f"Health check passed! HTTP Status Code: {http_code}")
            return True
        else:
            log(f"Health check failed. Received HTTP Status Code: {http_code}")
            return False
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        log(f"Health check failed due to an error: {e}")
        return False

def stop_container():
    log("Stopping container due to failed health check.")
    try:
        subprocess.run(
            ['docker', 'stop', CONTAINER_NAME],
            check=True
        )
        log(f"Container '{CONTAINER_NAME}' stopped successfully.")
    except subprocess.CalledProcessError as e:
        log(f"Failed to stop container: {e.stderr.strip()}")
        sys.exit(1)

def main():
    if container_is_running():
        log(f"Container '{CONTAINER_NAME}' is already running. Performing health check.")
    else:
        start_or_create_container()

    if not perform_health_check():
        log("Health check failed. Initiating container stop and cleanup.")
        stop_container()
        sys.exit(1)

if __name__ == "__main__":
    main()
