
import os
import re

src_dir = '/Users/diegoj/repos/djanban/src'

# Regex to match ForeignKey/OneToOneField and its arguments
# This is a heuristic and might miss complex cases, but covers standard usage.
# We look for models.ForeignKey( ... , on_delete=models.CASCADE)
# We want to insert on_delete=models.CASCADE if it's missing.

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Pattern matches: models.ForeignKey( match_group_1 , on_delete=models.CASCADE)
    # using dotall to handle multilines
    pattern = re.compile(r'(models\.(?:ForeignKey|OneToOneField)\s*\()([^)]+)(\))', re.DOTALL)

    def replacer(match):
        prefix = match.group(1)
        args_str = match.group(2)
        suffix = match.group(3)
        
        # Check if we already have on_delete
        if 'on_delete' in args_str:
            return match.group(0) # No change
        
        # Add on_delete
        # We append it to the args.
        # Check if args_str ends with comma
        clean_args = args_str.strip()
        if clean_args.endswith(','):
             new_args = f"{args_str} on_delete=models.CASCADE"
        else:
             new_args = f"{args_str}, on_delete=models.CASCADE"
             
        return f"{prefix}{new_args}{suffix}"

    new_content = pattern.sub(replacer, content)
    
    if new_content != content:
        print(f"Updating {filepath}")
        with open(filepath, 'w') as f:
            f.write(new_content)

for root, dirs, files in os.walk(src_dir):
    for filename in files:
        if filename.endswith('.py'):
            process_file(os.path.join(root, filename))
