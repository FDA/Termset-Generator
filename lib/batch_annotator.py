"""
Class to annotate multiple documents with ScispaCy and accumulate results.

The BatchAnnotator class loads ScispaCy and then lets you annotate documents
from a CSV file that contains multiple documents to annotate at once. The class
then saves the "batch" results from those documents for viewing with
termset_generator.py.
"""
from collections import defaultdict
import json
import re

import pandas as pd

from lib.scispacy_annotator import SciSpacyAnnotator

# Modifiers of terms to exclude
stopwords = ["denied", "denies", "her", "his", "negative", "no"]


class BatchAnnotator:
    """
    Annotate multiple documents with ScispaCy and save results.
    """
    def __init__(self, linker="umls"):
        """
        Constructor.

        Parameters
        ----------
        linker (str)
            Which ScispaCy thesaurus to load
        """
        self.annotator = SciSpacyAnnotator(linker=linker)
        self.docs = list()
        self._terms = defaultdict(dict)
        self.term_names = dict()
        self.verbose = True
        self.encoding = "utf-8"

        self.regex_upper = re.compile(r"^[A-Z]+$")

    @property
    def terms(self):
        return self._terms

    def load_csv(self, csv_filename, encoding="utf-8", text_column="TEXT"):
        """
        Load a CSV with medical text for annotating.

        Parameters
        ----------
        csv_filename: str
            Path to the CSV file to load
        encoding: str
            A valid Python file encoding (ascii, latin1, utf-8, etc.)
        text_column: str
            Name of the column that contains the medical text

        Returns
        -------
        Number of rows (documents) loaded
        """
        if self.verbose:
            print("Reading", csv_filename)

        # Use pandas to read the csv (one line of code)
        try:
            df = pd.read_csv(csv_filename, encoding=encoding)
        except UnicodeDecodeError:
            raise RuntimeError("File encoding does not appear to be %s - specify a different encoding." % encoding)

        df[text_column] = df[text_column].astype(str)
        df[text_column] = df[text_column].apply(lambda x: self.fixup(x))

        # Keep the documents
        self.docs = list(df[text_column])

        if self.verbose:
            print("Loaded %d docs" % len(self.docs))

        return len(self.docs)

    @staticmethod
    def fixup(text):
        """
        Cleanup text by converting common non-ASCII characters to their
        ASCII equivalents.
        """
        
        try:
            # These appear like \u00e2\u0092 in JSON
            text = text.replace("\xc2\x91", "'")  # Stylized quote
            text = text.replace("\xc2\x92", "'")  # Stylized quote
            text = text.replace("\xc2\x93", '"')  # Stylized double quote
            text = text.replace("\xc2\x94", '"')  # Stylized double quote
            text = text.replace("\u2013", "-")  # Double dash
            text = text.replace("\u201c", '"')  # Stylized double quote
            text = text.replace("\u201d", '"')  # Stylized double quote
        except AttributeError:
            print(type(text))
            pass

        return text

    def annotate(self, max_docs=None, output_file=None):
        """
        Annotate the loaded docs with scispaCy.

        Parameters
        ----------
        max_docs: int
            Optional max number of docs to process
        output_file: str
            Optional output file to save to (JSON)

        Returns
        -------
        Terms found (concepts and text found)

        Term structure is a dict with this pattern, indexed by CUID:

          "C0020538": {
            "name": "Hypertensive disease",
            "terms": [
              {
                "text": "hypertension",
                "score": 1.0,
                "count": 3
              },
              {
                "text": "HTN",
                "score": 1.0,
                "count": 1
              },
              {
                "text": "mild hypertension",
                "score": 0.8015103340148926,
                "count": 1
              },
            ]
          }
        """

        # Start fresh
        self._terms.clear()

        for i, text in enumerate(self.docs):
            if self.verbose:
                print("Document %d of %d" % (i + 1, len(self.docs)))

            # Run ScispaCy
            terms = self.annotator.annotate(text)

            # Add any new terms that were found
            for cuid, obj in terms.items():

                # Start a new concept ID if needed
                if cuid not in self._terms:
                    self._terms[cuid] = dict()
                    self._terms[cuid]["name"] = obj["name"]
                    self._terms[cuid]["terms"] = list()

                # Now add the terms to the concept
                for term in obj["terms"]:
                    # Get the term text and standardize on lowercase, unless an acronym
                    if not self.regex_upper.match(term["text"]):
                        term["text"] = term["text"].lower()

                    # Discard negations and other noise
                    words = term["text"].lower().split()
                    if len(words) == 0:
                        continue
                    elif words[0] in stopwords:
                        continue

                    # Add unique ones, case insensitive (favor lowercase)
                    add = True
                    for existing in self._terms[cuid]["terms"]:
                        if existing["text"] == term["text"]:
                            # Already have it
                            existing["count"] += 1
                            add = False
                            break
                        elif existing["text"] == term["text"].lower():
                            # Already have lowercase version
                            existing["count"] += 1
                            add = False
                            break
                        elif existing["text"].lower() == term["text"]:
                            # Already have uppercase version - keep lowercase
                            existing["count"] += 1
                            existing["text"] = existing["text"].lower()
                            add = False
                            break
                        else:
                            # Look at next term
                            pass
                    if add:
                        self._terms[cuid]["terms"].append(term)

            # Periodically update the output file
            if output_file and (i + 1) % 50 == 0:
                self._save(output_file)

            # Stop if there is a requested limit and it is reached
            if max_docs and (i + 1) >= max_docs:
                break

        # Write the final output file
        if output_file:
            self._save(output_file)

        return self._terms

    def _save(self, output_file):
        """
        Internal method to save the annotations to a JSON file.

        Parameters
        ----------
        output_file (str)
            Output filename

        Returns
        -------
        void
        """
        with open(output_file, "w", encoding=self.encoding) as f:
            json.dump(self._terms, f, indent=2, ensure_ascii=False)

        if self.verbose:
            print("Wrote", output_file)
