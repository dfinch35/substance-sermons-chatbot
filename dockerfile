# Use Python 3.11 slim image (lightweight and fast)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy everything from your repo
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# (Optional but recommended) Pre-build the index on container start
# This ensures the Chroma DB is always fresh
RUN python -c "
import os
if not os.path.exists('./chroma_db'):
    print('Building index for the first time...')
    os.system('python src/build_index.py')
else:
    print('Chroma DB already exists')
"

# Start Chainlit
CMD ["chainlit", "run", "app.py", "-w", "--host", "0.0.0.0", "--port", "7860"]
