"""
Functions to support termset_generator.py
"""
import pandas as pd
from collections import defaultdict
import json


def load_concept_csv(concepts_file):
    """
    Load a concept file, containing concepts of interest, as a CSV.
    """
    df = pd.read_csv(concepts_file)

    return df


def load_concept_json(concepts_file):
    """
    Read a concept file as a JSON and formats it as a dataframe.
    """
    df = pd.read_json(concepts_file, orient="index")
    df = df.reset_index().rename(columns={"index": "concept"})
    df = df.melt(id_vars=["concept"], value_vars=df.columns[1:], value_name="cui")
    df = df.drop(["variable"], axis=1).dropna()

    return df


def load_saved_json(concepts_file):
    """
    Read a saved termset as a JSON to format it as a dataframe.
    """ 
    df = pd.read_json(concepts_file, orient="index")
    df = df.reset_index().rename(columns={"index": "concept"})
    df = df.melt(id_vars=["concept"], value_vars=df.columns[1:], value_name="term")
    df = df.drop(["variable"], axis=1).dropna()

    return df


def make_phrase_dict(jsonfile, concept_df, concept_list, confidence=0.0):
    """
    Create a dictionary of qualified spelling variations for each concept of interest.
    
    Parameters
    ----------
    jsonfile: JSON
        JSON file of annotated clinical notes generated from the 
        annotate_docs.py script 
    concept_df: dataframe
        pandas dataframe with 2 columns: ["concept", "cui"]
    concept_list: list
        concepts of interest, defined in sidebar widget
    confidence: float
        minimum confidence score to include spelling variation

    Returns
    -------
    phrase_dict: dict
        a dictionary with a key for every concept of interest and values 
        containing every concept's spelling variation and the count of the
        number of times each spelling variation appeared in the JSON file, 
        formatted as the following:        
        {"concept_name1": defaultdict(int, {"spelling1": count1,
                                            "spelling2": count2})}
    """
    jsonfile = json.loads(jsonfile.getvalue())

    # Get concepts of interest after user added/removed from side bar
    selected_concept_df = concept_df[concept_df["concept"].isin(concept_list)]

    phrase_dict = dict()

    # Iterate through concept, term, then spelling variation
    for concept_name in selected_concept_df["concept"].unique():
        counts = defaultdict(int)
        for term in selected_concept_df[selected_concept_df["concept"] == concept_name]["cui"]:
            if term in jsonfile:
                for spelling in jsonfile[term]["terms"]:
                    # Collect spelling and count for spellings that meets min confidence
                    if spelling["score"] >= confidence:
                        counts[spelling["text"]] = spelling["count"]
            phrase_dict[concept_name] = counts

    return phrase_dict
