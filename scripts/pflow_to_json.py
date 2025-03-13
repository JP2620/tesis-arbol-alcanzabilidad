import sys
import xmltodict
import json

def main():
    # Check that exactly two arguments (input and output files) are provided
    if len(sys.argv) != 3:
        print("Usage: python script.py input.xml output.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        # Read the XML file
        with open(input_file, 'r') as xml_file:
            xml_content = xml_file.read()
        
        # Convert XML to a Python dictionary
        data_dict = xmltodict.parse(xml_content)
        
        # Convert the dictionary to a JSON string with indentation for readability
        json_data = json.dumps(data_dict, indent=4)
        
        # Write the JSON string to the output file
        with open(output_file, 'w') as json_file:
            json_file.write(json_data)
        
        print(f"Conversion completed successfully! JSON saved to {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

