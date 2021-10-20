import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from lib.batch_annotator import BatchAnnotator


def main(csv_filename):
    batch_annotator = BatchAnnotator(linker="umls")

    output_filename = csv_filename.replace(".csv", ".json")

    batch_annotator.load_csv(csv_filename)
    batch_annotator.annotate(output_file=output_filename)
    print("Done annotating %s, output in %s" % (csv_filename, output_filename))


if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].endswith(".csv"):
        print("Specify a CSV file (.csv) to process")
    else:
        main(sys.argv[1])
