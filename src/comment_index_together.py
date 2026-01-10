
import os
import re

src_dir = '/Users/diegoj/repos/djanban/src/djanban/apps'

def process_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    in_block = False
    paren_count = 0
    
    for line in lines:
        stripped = line.strip()
        if not in_block:
            if 'index_together =' in line:
                in_block = True
                new_lines.append(f"# {line}")
                paren_count += line.count('(') - line.count(')')
                if paren_count == 0:
                    in_block = False
            else:
                new_lines.append(line)
        else:
            # Inside the block, comment out
            new_lines.append(f"# {line}")
            paren_count += line.count('(') - line.count(')')
            if paren_count <= 0:
                in_block = False
                
    content = "".join(new_lines)
    
    # Check if changed
    if content != "".join(lines):
        print(f"Updating {filepath}")
        with open(filepath, 'w') as f:
            f.write(content)

for root, dirs, files in os.walk(src_dir):
    for filename in files:
        if filename.endswith('.py'):
            process_file(os.path.join(root, filename))
