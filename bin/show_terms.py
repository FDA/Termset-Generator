"""
Show the concepts found by annotate_docs.py and stored in a JSON file.
"""
import json
import sys


def main():
    json_filename = sys.argv[1]
    with open(json_filename, "r") as f:
        js = json.load(f)

    # If no CUIDs provided show all
    if len(sys.argv) == 2:
        for cuid, terms in sorted(js.items(), key=lambda x: len(x[1]["terms"]), reverse=False):
            print("%s %s [%s]" % (cuid, js[cuid]["name"], ", ".join(t["text"] for t in js[cuid]["terms"])))
            print("")
    else:
        for cuid in sys.argv[2:]:
            if cuid in js:
                print("%s %s [%s]" % (cuid, js[cuid]["name"], ", ".join(t["text"] for t in js[cuid]["terms"])))
                print("")


if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].endswith(".json"):
        print("Specify an annotate_docs.py JSON output file (.json) to process")
    else:
        main()
