import appdirs
import os
import subprocess
from pathlib import Path

def get_servers_dir():
    """Get the servers directory from settings.txt or return default"""
    config_dir = appdirs.user_config_dir("grassy")
    settings_file = os.path.join(config_dir, "settings.txt")
    data_dir = appdirs.user_data_dir("grassy")
    default_dir = os.path.join(data_dir, "servers")
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                saved = f.read().strip()
                if saved:
                    return saved
        except:
            pass
    
    os.makedirs(default_dir, exist_ok=True)
    
    # Save the default path to settings.txt
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(settings_file, "w") as f:
            f.write(default_dir)
    except:
        pass
    
    return default_dir


def save_servers_dir(path):
    """Save the servers directory to settings.txt"""
    config_dir = appdirs.user_config_dir("grassy")
    settings_file = os.path.join(config_dir, "settings.txt")
    
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(settings_file, "w") as f:
            f.write(path)
        return True
    except:
        return False

def kill_process_on_port(port=25565):
    import signal
    import platform

    system = platform.system()

    try:
        if system == "Windows":
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )

            pids = set()
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    pids.add(parts[-1])

            for pid in pids:
                subprocess.run(f'taskkill /PID {pid} /F', shell=True)

            return len(pids)

        else:
            result = subprocess.run(
                f"lsof -t -i:{port}",
                shell=True,
                capture_output=True,
                text=True
            )

            pids = result.stdout.strip().split()

            for pid in pids:
                if pid:
                    os.kill(int(pid), signal.SIGKILL)

            return len(pids)

    except Exception as e:
        print(f"Error killing process on port {port}: {e}")
        return 0

def is_java_installed():
    try:
        result = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except FileNotFoundError:
        # Try fallback for Windows
        try:
            result = subprocess.run(
                ["where", "java"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            return result.returncode == 0
        except:
            return False
