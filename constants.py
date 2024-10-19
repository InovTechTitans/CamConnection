import os

URL = f"rstp://{os.getenv('USERNAME')}:{os.getenv('PASSWORD')}@{os.getenv('IP')}:{os.getenv('PORT')}/{type}"
