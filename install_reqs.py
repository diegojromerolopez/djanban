
import subprocess
import sys

with open('src/requirements.txt', 'r') as f:
    requirements = f.readlines()

failed = []
installed = []

for req in requirements:
    req = req.strip()
    if not req or req.startswith('#'):
        continue
    print("Installing %s..." % req)
    try:
        subprocess.check_call(['./venv27/bin/pip', 'install', req])
        installed.append(req)
    except subprocess.CalledProcessError:
        print("Failed to install %s" % req)
        failed.append(req)

print("\nInstalled: %d" % len(installed))
print("Failed: %d" % len(failed))
for f in failed:
    print("  - %s" % f)
