FROM registry.access.redhat.com/ubi8/python-39@sha256:6b0a73679bad8510b017bb95e411bd4a7d3ee7d3515d030bba3b710254921f23


COPY . /src

WORKDIR /src

USER root

# Create a virtual environment

# Activate the virtual environment

# Install dependencies in the virtual environment
RUN pip3 install -r requirements_sql.txt

EXPOSE 8000

CMD ["/bin/bash", "startup.sh"]
