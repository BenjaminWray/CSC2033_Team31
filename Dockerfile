# Use python
FROM python:latest

# Create working directory
WORKDIR /app

# Install requirements
ADD requirements.txt .
RUN pip install -r requirements.txt

# Add project files
ADD flaskr flaskr
ADD tests tests

# Run flask application
EXPOSE 5000
CMD ["python", "-m", "flask", "--app=flaskr/app.py", "run", "--host=0.0.0.0", "--port=5000"]