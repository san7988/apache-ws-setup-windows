activate_this = "<path-to_python_env>/Scripts/activate_this.py"
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
import sys

sys.path.insert(0, <path_to_app_root_dir>)
 
from app import app as application