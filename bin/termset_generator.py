"""
Run the Termset Generator user interface from the command line. 

This file contains the front-end code to run the Termset Generator, a tool
which generates a "termset", or list of synonyms and spelling variations
for a given "concept of interest", or medical term.

Usage:
streamlit run termset_generator.py
"""
import json
import os

import pandas as pd
import streamlit as st
import streamlit_functions as sf


def load_concept_file(concept_file):
    """
    Read in the concept file as either a CSV or JSON.
    """
    if concept_file.name.lower().endswith(".csv"):
        return sf.load_concept_csv(concept_file)
    elif concept_file.name.lower().endswith(".json"):
        return sf.load_concept_json(concept_file)
    else:
        # Should never get here
        st.info(
            'Unsupported filename "%s".' % concept_file.name)
        return None


def save_termset(concept, terms, filename):
    """
    Save the termset as a JSON if filepath exists. 
    """
    try:
        with open(filename, "w") as f:
            json.dump({concept: terms}, f, indent=4)
            st.success(f"{filename} saved successfully!")
    except FileNotFoundError:
        st.text("File path does not exist. Correct or remove file path to save.")


def show_save_controls(concept, terms, selected, button_name, suffix, default_dir):
    """
    Display options to save a termset as a JSON.
    """
    opt_pathname = st.text_input("Specify file path to save JSON into. (Optional)",
                                 key=concept + str(terms) + "specify_path")

    if st.button("Save JSON", key=concept + str(terms) + button_name):
        # Assign specified directory
        if len(opt_pathname) > 0:
            default_dir = os.path.join("..", opt_pathname)
        
        # If directory does not exist, create directory
        if not os.path.isdir(default_dir):
            os.mkdir(default_dir)
            st.success(f"Created folder: {default_dir}")
        
        save_name = os.path.join(default_dir, concept + suffix)
        save_termset(concept, terms, save_name)


def show_top_sidebar():
    """
    Display options to use "Generate" or "Review" mode.
    """
    st.sidebar.image("../static/logo.png", use_column_width=True)
    st.sidebar.header("Termset Generator")
    st.sidebar.markdown(
        """
        Generate candidate text spans from a corpus of annotated medical notes.
        """
    )

    mode = st.sidebar.radio("Select Generate or Review mode", ("Generate", "Review"))

    return mode


def show_bottom_sidebar():
    """
    Display Acknowledgements.
    """
    st.sidebar.markdown(
        """
        ### Acknowledgements
        Built by IBM as a part of FDA's Biologics Effectiveness and Safety Initiative (BEST)
        """
    )
    st.sidebar.image("../static/ibm_fda_logos.png", use_column_width=True)
    st.sidebar.markdown(
        """
        NLP pipeline built with [spaCy](https://spacy.io/) and [ScispaCy](https://allenai.github.io/scispacy/).
        UI adapted from UI at [ScispaCy](https://scispacy.apps.allenai.org).
        """
    )


def show_terms(concept, terms):
    """
    Display spelling variations for a given concept of interest to add or remove.
    """
    st.subheader(concept)
    terms.sort()
    
    # Allow user to add/remove spelling variations
    selected = st.multiselect("Terms found in corpus", terms, default=terms, key=concept + "_ms")
    selected.sort()

    return selected


def show_results_controls(concept, terms, selected):
    """
    Display options to review and edit each termset.
    """
    # Show JSON of selected terms
    if st.button("Show JSON", key=concept + str(terms) + "_button"):
        st.json({concept: selected})

    # Manually add new terms
    new_term = st.text_input(
        label="If you would like to manually add custom terms, enter a comma separated list below. (Optional)",
        key=concept + str(terms) + "_add_term")
    if new_term != "":
        new_terms = [x.strip() for x in new_term.split(",")]
        terms.extend(new_terms)
        terms.sort()
        df_2 = pd.DataFrame({"Final Termset": terms})
        st.write(df_2)

    return terms


def generate_mode():
    """
    Run Generate mode functionality. 
    """
    # Controls to get the corpus, confidence, and concepts for search
    corpus_file = st.sidebar.file_uploader("Annotated file", type="json")
    confidence = st.sidebar.slider("Confidence", min_value=0.0, value=0.9)
    file_types = ["csv", "json"]
    concept_file = st.sidebar.file_uploader("Concept file", type=file_types)

    # Controls for acknowledgements
    show_bottom_sidebar()

    # If a concept file is uploaded, load it into a DataFrame
    concept_df = None
    if concept_file:
        concept_df = load_concept_file(concept_file)

    # If we have both the corpus and concepts, get the phrases that are found
    phrase_dict = dict()
    if corpus_file and concept_file is not None:
        with st.spinner("Processing..."):
            try:
                concepts = list(concept_df["concept"].unique())
                concept_list = st.sidebar.multiselect("Concepts", concepts, default=concepts)
                phrase_dict = sf.make_phrase_dict(corpus_file, concept_df, concept_list, confidence)
            except ValueError:
                st.subheader("Annotated file does not contain any of the concepts of interest.")
    
    # Specify the directory for saved termsets            
    default_dir = "../Saved Termsets/"
   
    # Show the found phrases
    for concept, term_counts in phrase_dict.items():
        # Buttons for the phrases
        terms = list(term_counts.keys())
        selected = show_terms(concept, terms)

        # Phrase counts
        df = pd.DataFrame.from_dict(term_counts, orient="index", columns=["count"])
        df["term"] = df.index
        df = df[["term", "count"]]  # Reorder columns for UI
        # Reorder the dataframe by count descending, term alphabetically
        df.sort_values(by=["count", "term"], ascending=[False, True], inplace=True)
        df = df.reset_index(drop=True)
        st.dataframe(df)

        # Controls to show and modify the results
        terms = show_results_controls(concept, terms, selected)

        # Control to save the results
        show_save_controls(concept, terms, selected, "generate_save_button", " termset.json", default_dir)


def review_mode():
    """
    Run Review mode functionality.
    """
    # Controls to get the concepts for search
    saved_file = st.sidebar.file_uploader("Saved \"Generate\" results file", type="json")

    # Controls for acknowledgements
    show_bottom_sidebar()

    if saved_file:
        default_dir = "../Reviewed Termsets/"
        concept_df = sf.load_saved_json(saved_file)
        for concept, group in concept_df.groupby("concept"):
            terms = sorted(list(group["term"].unique()))

            # Buttons for the phrases
            selected = show_terms(concept, terms)

            df = pd.DataFrame({"Original Values": selected})
            st.write(df)

            # Controls to show and modify the results
            terms = show_results_controls(concept, terms, selected)

            # Control to save the results
            show_save_controls(concept, terms, selected, "review_save_button", " termset_reviewed.json", default_dir)


if __name__ == "__main__":
    mode = show_top_sidebar()

    if mode == "Generate":
        generate_mode()
    elif mode == "Review":
        review_mode()
