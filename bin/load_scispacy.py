import spacy
from scispacy.linking import EntityLinker

print("Installing ScispaCy ontologies. Please wait...")

nlp = spacy.load("en_core_sci_sm")

config = dict()
config["linker_name"] = "umls"
config["resolve_abbreviations"] = True
nlp.add_pipe("scispacy_linker", config=config)
linker = nlp.get_pipe("scispacy_linker")

