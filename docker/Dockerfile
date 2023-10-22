# Official python:3.12 image
FROM python:3.12
LABEL maintainer="Ahmed Ashraf <ahmedabdou1410@gmail.com>"

# Set the working directory to /app
WORKDIR /app

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# https://docs.python.org/3/using/cmdline.html#cmdoption-u
# Prevents Python from buffering stdout and stderr
ENV PYTHONBUFFERED 1

# Update apt-get & clean up.
RUN apt-get update \
    && apt-get clean

# Upgrade pip.
RUN pip3 install --upgrade pip

# Copy the current directory contents into the container at /app
COPY ../requirements/ app/requirements/

# Install dependencies in prod.txt
RUN pip3 install --no-cache-dir --upgrade -r app/requirements/prod.txt

# Copy the current directory contents into the container at /app
COPY .. /app

# Set the PYTHONPATH to the current directory
# This is needed to import the app module from python scripts called from the entrypoint.sh
# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH
ENV PYTHONPATH=.

# Make the bash scripts executable
RUN chmod +x ./scripts/*.sh

# Run entrypoint.sh before starting the server
ENTRYPOINT [ "./scripts/entrypoint.sh" ]

# Run start.sh to launch the server
CMD ["./scripts/start.sh"]
