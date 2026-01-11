
import os

def bootstrap_tests():
    src_root = "src/djanban"
    test_root_unit = "src/djanban/tests/unit"
    test_root_integration = "src/djanban/tests/integration"
    
    for root, dirs, files in os.walk(src_root):
        if "tests" in root:
            continue
        if "static" in root and "apps" not in root:
            continue
            
        rel_path = os.path.relpath(root, src_root)
        if rel_path == ".":
            rel_path = ""
            
        for d in [test_root_unit, test_root_integration]:
            target_dir = os.path.join(d, rel_path)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            init_file = os.path.join(target_dir, "__init__.py")
            if not os.path.exists(init_file):
                open(init_file, 'a').close()
        
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_rel_path = os.path.join(rel_path, file)
                
                # Unit test file
                unit_test_file = os.path.join(test_root_unit, module_rel_path)
                if not os.path.exists(unit_test_file):
                    with open(unit_test_file, 'w') as f:
                        f.write("# -*- coding: utf-8 -*-\n")
                        f.write("import unittest\n")
                        # Construct module name
                        mod_name = module_rel_path.replace("/", ".").replace(".py", "")
                        if mod_name.startswith("."): mod_name = mod_name[1:]
                        f.write("from djanban.%s import *\n\n" % mod_name)
                        f.write("class Test%s(unittest.TestCase):\n" % file.replace(".py", "").capitalize().replace("_", ""))
                        f.write("    pass\n")

                # Integration test file
                int_test_file = os.path.join(test_root_integration, module_rel_path)
                if not os.path.exists(int_test_file):
                    with open(int_test_file, 'w') as f:
                        f.write("# -*- coding: utf-8 -*-\n")
                        f.write("import unittest\n")
                        f.write("from django.test import TestCase\n\n")
                        f.write("class Test%sIntegration(TestCase):\n" % file.replace(".py", "").capitalize().replace("_", ""))
                        f.write("    pass\n")

if __name__ == "__main__":
    bootstrap_tests()
