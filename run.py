from app import create_app
from dotenv import load_dotenv
import os
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 5000), debug=True)
