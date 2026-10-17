import sys
import os

# Add mocks to sys.path
MOCKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mocks')
# Insert at position 0 to override any installed packages if present, 
# though we expect them to be missing.
sys.path.insert(0, MOCKS_DIR)

# Mock statsmodels modules structure since they are often nested
# ensure statsmodels.tsa exists as a package
import statsmodels
if not hasattr(statsmodels, 'tsa'):
    import statsmodels.tsa.api

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djanban.settings")
    from django.core.management import execute_from_command_line
    if 'test' not in sys.argv:
        sys.argv.append('test')
    execute_from_command_line(sys.argv)
