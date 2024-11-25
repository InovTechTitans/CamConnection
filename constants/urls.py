import os

URL = f"rtsp://{os.getenv('USERNAME')}:{os.getenv('PASSWORD')}@{os.getenv('IP')}:{os.getenv('PORT')}/cam/realmonitor?channel=1&subtype=0"
