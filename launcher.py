# launcher.py - starts the real app
import os
import subprocess
import logging

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".log")
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, "datawizard_launcher.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(base, "app", "DataWizardApp", "DataWizardApp.exe")
    logging.info(f"Launcher invoked. Looking for {target}")
    if not os.path.exists(target):
        logging.error("Executable not found.")
        return
    subprocess.Popen([target], cwd=os.path.dirname(target))

if __name__ == '__main__': main()
