import os
from dotenv import load_dotenv

# Simulate inherited env var from parent uvicorn process
os.environ['QUESTRADE_REFRESH_TOKEN'] = 'old_token'

# User updates .env file
with open('.env.test', 'w') as f:
    f.write('QUESTRADE_REFRESH_TOKEN="new_token"\n')

# load_dotenv standard behavior
load_dotenv('.env.test')
print("Without override:", os.getenv('QUESTRADE_REFRESH_TOKEN'))

# load_dotenv with override
load_dotenv('.env.test', override=True)
print("With override:", os.getenv('QUESTRADE_REFRESH_TOKEN'))
