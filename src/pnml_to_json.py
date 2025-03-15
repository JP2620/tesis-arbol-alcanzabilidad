import argparse
import xml.etree.ElementTree as ET
import json
import sys

def parse_pnml(pnml_path):
    # Parse the PNML file.
    try:
        tree = ET.parse(pnml_path)
    except Exception as e:
        sys.exit(f"Error parsing PNML file: {e}")
    
    root = tree.getroot()
    # Find the page element (assuming a single page)
    page = root.find(".//page")
    if page is None:
        sys.exit("No <page> element found in the PNML file.")

    # Get places and their initial markings.
    places = []
    marcado_inicial = []
    for place in page.findall("place"):
        place_id = place.get("id")
        places.append(place_id)
        # Find the initialMarking/text element.
        im_element = place.find(".//initialMarking/text")
        if im_element is not None and im_element.text is not None:
            try:
                marking = int(im_element.text.strip())
            except ValueError:
                marking = 0
        else:
            marking = 0
        marcado_inicial.append(marking)

    # Get transitions.
    transitions = []
    for transition in page.findall("transition"):
        trans_id = transition.get("id")
        transitions.append(trans_id)

    # Initialize incidence matrices with zeros.
    num_places = len(places)
    num_transitions = len(transitions)
    incidence_positiva = [[0 for _ in range(num_transitions)] for _ in range(num_places)]
    incidence_negativa = [[0 for _ in range(num_transitions)] for _ in range(num_places)]
    
    # Create dictionaries for fast index lookup.
    place_idx = {pid: idx for idx, pid in enumerate(places)}
    trans_idx = {tid: idx for idx, tid in enumerate(transitions)}
    
    # Process arcs.
    for arc in page.findall("arc"):
        source = arc.get("source")
        target = arc.get("target")
        # Get the weight from the inscription if present; default is 1.
        inscription = arc.find(".//inscription/text")
        try:
            weight = int(inscription.text.strip()) if inscription is not None and inscription.text is not None else 1
        except ValueError:
            weight = 1
        
        # Determine type of arc by checking if source/target are in places or transitions.
        if source in place_idx and target in trans_idx:
            # Arc from a place to a transition (consumption).
            i = place_idx[source]
            j = trans_idx[target]
            incidence_negativa[i][j] = weight
        elif source in trans_idx and target in place_idx:
            # Arc from a transition to a place (production).
            i = place_idx[target]
            j = trans_idx[source]
            incidence_positiva[i][j] = weight
        else:
            print(f"Skipping arc {arc.get('id')}: unmatched source/target.")
    
    return {
        "incidence_positiva": incidence_positiva,
        "incidence_negativa": incidence_negativa,
        "marcado_inicial": marcado_inicial
    }

def main():
    parser = argparse.ArgumentParser(
        description="Transform a PNML file into a JSON file containing incidence matrices and the initial marking."
    )
    parser.add_argument("pnml_path", help="Path to the input PNML file")
    parser.add_argument("output_json", help="Filename for the output JSON file")
    args = parser.parse_args()

    result = parse_pnml(args.pnml_path)

    # Write the JSON file.
    try:
        with open(args.output_json, "w") as out_file:
            json.dump(result, out_file, indent=4)
        print(f"JSON successfully written to {args.output_json}")
    except Exception as e:
        sys.exit(f"Error writing JSON file: {e}")

if __name__ == '__main__':
    main()

