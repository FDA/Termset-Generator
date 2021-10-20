# Termset Generation
The termset generator lets you discover the ways in which medical concepts are written
in a corpus of documents. NIH's UMLS contains the official spellings but often in practice
people use acronyms and alternate spellings that are not reflected in UMLS. Termset
generator leverages UMLS plus a machine learning NLP annotator called "ScispaCy" to find
these acronyms and alternate spellings as used in documents you provide.

To be most useful, run termset generator against a large set of documents - ideally
thousands - to find these spellings. Thousands are typically required because most medical
concepts appear in only a small subset of documents. If you can first select that subset,
such as by providing encounter notes for a particular specialty or for patients with a
known diagnosis, then fewer documents could be used as the relevant medical concepts should
be much more common in those.

## Table of Contents
[Introduction](#Introduction)

[Getting Started](#GettingStarted)

[Usage](#Usage)

[Requirements](#Requirements)

[Docker](#Docker)

[Acknowledgements](#Acknowledgements)


## Introduction

The Termset Generator is an open-source tool designed to rapidly develop lists of terms, or termsets, for computational phenotypes from a given corpus of clinical notes. The tool leverages natural language processing for data-driven generation of unstructured termsets, by converting clinical notes into Unified Medical Language System (UMLS) concepts and automatically extracting candidate concept spans. Its user-friendly interface has two modes, 'Generate' and 'Review', which respectively allows users to create and customize termsets for concepts of their interest.

By employing a computational model to generate termsets, this tool is able to conserve expensive time needed from subject matter experts, reduce researcher bias, and extract terms that correspond to the UMLS concepts even when notes are low quality and have a variety of misspellings and varying usage of abbreviations and acronyms. The resulting termsets may then be shared with and modified for use by new institutions using this tool to reflect the unique ways clinical notes are written in a different locale.

## Getting Started
NOTE: To run termset generator in Docker, follow the instructions for [Docker](#Docker).

Verify you have Python 3 installed (termset generator was developed with Python 3.8.) It is also recommended to create a
python virtual environment to ensure a clean install.

Install required termset generator Python packages:
```
pip install -r requirements.txt
```

Download ScispaCy's NLP model:
```
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_sm-0.4.0.tar.gz
```

Download ScispaCy's UMLS annotator (takes several minutes):
```
python bin/load_scispacy.py
```

Test ScispaCy by annotating the sample documents. Note that
loading UMLS can take over a minute. You may also see 
warnings from ScispaCy.
```
python bin/annotate_docs.py samples/sample_docs.csv
```

Test the UI:
```
cd bin
streamlit run termset_generator.py
```
Navigate to the UI in your browser. Load the ScispaCy annotated file
from `samples/sample_docs.json`. Load the sample concepts file
from `samples/sample_concepts.json`. Verify the UI shows spellings
for respiratory distress.

## Usage
### Creating a CSV of Medical Documents
The termset generator expects a CSV file that contains the medical documents to annotate, one document per row. There are various ways to create a CSV, either programmatically or manually. You can use Microsoft Excel or a similar spreadsheet and paste the documents, one on each row, for example.The first row must be the column headers. The default name for the text column is "TEXT". More documents in the CSV mean the termset generator can find more spelling variations. However, processing time is longer.

If you would like to test the Termset Generator's natural language processing [annotation script](bin/annotate_docs.py) and [user interface](bin/termset_generator.py) on deidentified clinical data, you can create a [Mimic Membership](https://mimic.mit.edu/#td-block-1) and can download sample medical notes. Be sure to format the sample file as a CSV with a column named TEXT.


### Pre-processing: Annotating the CSV with Natural Language Processing
When the CSV of documents is ready, run `annotate_docs.py` with that CSV to find medical terms in those documents.

```
python bin/annotate_docs.py my_csv_file.csv
```

Output is written to the same path but with ".json" instead of ".csv". The output file contains the UMLS concepts and their spellings as found in the CSV documents. You can then load that JSON file into the termset generator UI to explore concepts and spellings. Note that the UMLS ontology is large and may take 90 seconds to load.

To review specific concepts in your Annotated JSON file, run the following code with the Concept Unique Identifiers (CUI) of your interest written in double quotations.

```
python bin/show_terms.py my_json_file.json "yourCUIofInterest1" "yourCUIofInterest2"
```

### Running the Termset Generator User Interface to Generate Termsets

To change your directory and open the Termset Generator UI, run the following two lines of code:
```
cd termset_generation/bin
streamlit run termset_generator.py
```
The Termset Generator should display in your browser with a sidebar to upload your files. Select which mode you would like to work with: 'Generate' or 'Review'.

#### Generate Mode
Generate Mode allows users to generate and download termsets for each concept of interest. Users must upload an Annotated JSON file, produced from the [annotate_docs.py script](bin/annotate_docs.py), and a Concept file, formatted as a JSON, which contains concepts of interest with their corresponding CUIs. To view a sample of the Concept file as a JSON, click [here](samples/sample_concept_file.json). Once the Concept File is uploaded, concepts of interest will display in the field below, where users can deselect concepts as they choose. Users may also indicate the minimum confidence value for terms to be considered a synonym for concepts of interest; the default confidence level is .9. 

When both files are uploaded, each concept of interest will appear in bold, and all terms that were detected as synonyms in the medical notes will display in the fields below. The user may manually deselect and add additional terms for each concept. Once the user is satisfied with the terms that were detected from the annotated medical documents, the user will save the termset, by clicking 'Save JSON', in which the termset will download as a JSON. In the above the 'Save JSON' button, users are able to update the filepath they would like to save to as well. This downloaded termset may be used within the Termset Generator's Review mode.

#### Review Mode
Review Mode is designed for users to upload a previously generated termset, which they downloaded as a JSON under the Generate mode. Once the file is uploaded, users can review, add and/or delete terms, and save the edited termset for the concept of interest. 

## Requirements
### Software Requirements
- [ScispaCy](https://github.com/allenai/scispacy). (Note that ScispaCy will download the UMLS ontology the first time it is used.)
- en_core_sci_sm (ScispaCy NLP model)
- pandas

### Hardware Requirements
- 16 GB RAM recommended

## Docker
Termset generator may be easier to run in Docker, as you won't have to install Python and ScispaCy. A computer with
at least 16 GB of RAM is recommended as 8 GB may not be enough.

To use Docker, first download and install Docker from http://www.docker.com. Then, build and run the Docker image with these commands:
- docker build -t termset_generation .
- docker run -d -p 8501:8501 -v /tmp:/data termset_generation

The run command defaults to looking in /tmp (Mac/Linux) on your computer for CSV files that you wish to annotate. Change
that path as desired to look in a different directory. For Windows, the syntax is similar to this:
- docker run -d -p 8501:8501 -v "/c/windows/temp":/data termset_generation

For convenience, sample scripts are provided (modify run_docker as needed to set your path):
- build_docker.sh (Mac/Linux), build_docker.bat (Windows)
- run_docker.sh (Mac/Linux), run_docker.bat (Windows)

Verify the Docker image is running and get its Docker name with this command:
- docker ps
The Docker image's name is at the end and is the phrase with two words concatenated with underscore. Note that the name
changes each time you re-build the image.

The last step is to use the Docker image to annotate your CSV file. This consists of first logging into the Docker image
and then running annotate_docs.py as described above. To login to the Docker image, use this command, replacing "word1_word2" with your Docker image's name:
- docker exec -it word1_word2 /bin/bash

You should then see a Linux bash login with the "#" symbol. Make sure you have a CSV file in the shared directory specified in the docker run command (e.g. /tmp). Then, annotate that CSV with this command, replacing "my CSV file" with your CSV filename in that directory:
- python bin/annotate_docs.py /data/<my CSV file>

You can also verify that it's there and that Docker sees it by listing that directory:
- ls -l /data

Termset generator should run inside Docker and output the annotated JSON file in the same directory. You can then exit the Docker image by typing "exit" or Ctrl-D.



## Acknowledgements
The Termset Generator was built by IBM as a part of FDA's Biologics Effectiveness and Safety Initiative (BEST).
