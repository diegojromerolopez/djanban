
import os
import re

base_path = '/Users/diegoj/repos/djanban/src/djanban/apps'

for dirname in os.listdir(base_path):
    dirpath = os.path.join(base_path, dirname)
    if not os.path.isdir(dirpath):
        continue
    
    apps_py = os.path.join(dirpath, 'apps.py')
    if not os.path.exists(apps_py):
        print(f"Skipping {dirname}, no apps.py")
        continue

    print(f"Checking {dirname}...")
    with open(apps_py, 'r') as f:
        content = f.read()
    
    expected_name = f'djanban.apps.{dirname}'
    
    # We look for: name = 'something'
    # and replace it with name = 'djanban.apps.dirname'
    
    new_content = re.sub(
        r"name\s*=\s*['\"]([^'\"]+)['\"]",
        f"name = '{expected_name}'",
        content
    )
    
    if new_content != content:
        print(f"Updating {dirname} apps.py")
        with open(apps_py, 'w') as f:
            f.write(new_content)
    else:
        print(f"No changes for {dirname}")
