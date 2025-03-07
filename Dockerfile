# Use python
FROM python:latest

# Install requirements
ADD requirements.txt .
RUN pip install -r requirements.txt

# Create working directory
WORKDIR /flaskr

# Add project files
ADD flaskr .

# Run flask application
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]