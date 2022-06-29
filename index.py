'''from dotenv import load_dotenv
import os

load_dotenv()
print(os.environ['FILE_PATH'])
'''

from src.pycode.dashboard import app


app.run_server(debug=True, host="0.0.0.0", port=8050) 