import dotenv
import os
import time

initial = time.time()
dotenv.load_dotenv()
key = os.environ.get('YANDEX_KEY')
print(time.time() - initial)