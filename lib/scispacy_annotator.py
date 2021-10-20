"""
Class for invoking ScispaCy.

The SciSpacyAnnotator class lets you load ScispaCy once and then repeatedly
invoke it to annotate documents.
"""
from collections import defaultdict

import spacy
from scispacy.linking import EntityLinker


class SciSpacyAnnotator:
    """
    Wrapper around ScispaCy for exporting terms.
    """

    def __init__(self, linker="umls", model="en_core_sci_sm", threshold=0.7):
        """
        Constructor.

        Parameters
        ----------
        linker (str)
            Which ScispaCy thesaurus to load
        model (str)
            Which ScispaCy model to load (small/medium/large)
        threshold (float)
            Min score to keep a term
        """
        self.threshold = threshold
        self.verbose = True

        if self.verbose:
            print("Loading", model)

        self.nlp = spacy.load(model)

        # Which terminology set to link to. Current choices:
        # umls   - UMLS
        # mesh   - NIH MeSH
        # rxnorm - RxNorm
        # go     - Gene Ontology
        # hpo    - Human Phenotype Ontology
        linker = linker

        if self.verbose:
            print("Loading %s linker..." % linker)

        # Configure the scispacy pipeline
        config = dict()
        config["linker_name"] = linker
        config["resolve_abbreviations"] = True
        self.nlp.add_pipe("scispacy_linker", config=config)

        # Get the linker so we can resolve concept IDs
        self.linker = self.nlp.get_pipe("scispacy_linker")

    def annotate(self, text):
        """
        Annotate text with ScispaCy and return the terms found.

        Parameters
        ----------
        text (str)
            Text to annotate

        Returns
        -------
        CUIDs with their names and term spellings
        """
        terms = defaultdict(dict)

        # Run ScispaCy
        doc = self.nlp(text)

        # Collect the concept IDs, terms, and scores
        for ent in doc.ents:
            for umls_ent in ent._.kb_ents:
                score = umls_ent[1]

                # Skip those with low scores
                if score < self.threshold:
                    continue

                # Get the term
                obj = self.linker.kb.cui_to_entity[umls_ent[0]]

                # Start a new concept ID if needed
                if obj.concept_id not in terms:
                    terms[obj.concept_id] = dict()
                    terms[obj.concept_id]["name"] = obj.canonical_name
                    terms[obj.concept_id]["terms"] = list()

                # Add the term
                d = dict()
                d["text"] = ent.text
                d["text"] = d["text"].replace("\r", " ").strip()
                d["text"] = d["text"].replace("\n", " ").strip()
                d["score"] = score
                d["count"] = 1
                terms[obj.concept_id]["terms"].append(d)

        return terms
