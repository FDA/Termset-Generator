#Python base image
FROM python:3.8
MAINTAINER Doug Billings dougbill@us.ibm.com

# Run from a directory other than root since we have our own /bin
WORKDIR /termset_generation

# Install all the files and directories we need
ADD bin/ bin/
ADD lib/ lib/
#ADD samples/ samples/
ADD static/ static/
ADD logo.png logo.png

# Expose streamlit port
EXPOSE 8501

# Install required non-Python OSS packages
#RUN apt-get update && apt-get install ghostscript imagemagick tesseract-ocr -y

# Not sure why the copy is needed but it is
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# Download ScispaCy NLP models
RUN pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_sm-0.4.0.tar.gz
RUN python bin/load_scispacy.py

# Start the workflow apps and REST API
# NOTE: This stays running. The docker image closes if this app ends (shouldn't).
#CMD sh bin/startup_docker.sh
CMD cd bin && streamlit run termset_generator.py < no_email.txt

