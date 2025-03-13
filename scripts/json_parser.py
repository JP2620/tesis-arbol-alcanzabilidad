import json
import sys
from typing import Dict

def main(input_file: str):
    # Load the original JSON from the given file
    with open(input_file, 'r') as f:
        data = json.load(f)

    places = data['document']['subnet']['place']
    transitions = data['document']['subnet']['transition']
    arcs = data['document']['subnet']['arc']
    petri_net_json: Dict = {}

    petri_net_json['places'] = []
    petri_net_json['transitions'] = []
    petri_net_json['arcs'] = []

    for i, place in enumerate(places):
        petri_net_json['places'].append(
            {
                "index": i,
                "type": "discrete",
                "initial_marking": int(place['tokens'])
            }
        )

    temporal: bool = False
    for i, transition in enumerate(transitions):
        petri_net_json['transitions'].append(
            {
                "index": i,
                "type": "immediate" if transition['timed'] == 'false' else "temporal",
                "guard": True,
                "event": True
            }
        )
        if transition["timed"] == "true":
            temporal = True

    for i, arc in enumerate(arcs):
        petri_net_json['arcs'].append(
            {
                "type": arc['type'],
                "from_place": False if arc['sourceId'][0] == 'T' else True,
                "source": int(arc['sourceId'][1]) - 1,
                "target": int(arc['destinationId'][1]) - 1,
                "weight": int(arc['multiplicity'])
            }
        )

    petri_net_json['network'] = {
        "id": "ejemplo-omegas",
        "amount_places": len(places),
        "amount_transitions": len(transitions),
        "time_scale": "millisecond",
        "is_temporal": temporal,
        "network_type": "discrete"
    }


    # Overwrite the original file with the new JSON schema
    with open(input_file, 'w') as f:
        json.dump(petri_net_json, f, indent=4)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py input_filename.json")
        sys.exit(1)
    input_filename = sys.argv[1]
    main(input_filename)
