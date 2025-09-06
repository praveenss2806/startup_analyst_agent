import json

def convert_json_to_json_lines(input_file_path, output_file_path):
    """
    Parses a single JSON object file and writes its contents
    as multiple JSON Lines to a new file.
    
    Args:
        input_file_path (str): The path to the original single-object JSON file.
        output_file_path (str): The path to the new JSON Lines output file.
    """
    try:
        with open(input_file_path, 'r') as f:
            data = json.load(f)

        rows = []
        
        # Extract the target startup data and add it as a row
        if 'target_startup' in data:
            rows.append(data['target_startup'])
        
        # Iterate through the competitors list and add each one as a new row
        if 'competitors' in data and isinstance(data['competitors'], list):
            for competitor in data['competitors']:
                rows.append(competitor)
        
        # Write the prepared data to the output file in JSON Lines format
        with open(output_file_path, 'w') as f:
            for row in rows:
                f.write(json.dumps(row) + '\n')
        
        print(f"Successfully converted data to JSON Lines and saved to '{output_file_path}'")
        
    except FileNotFoundError:
        print(f"Error: The file at '{input_file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file at '{input_file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Example Usage ---
# Replace with the actual path to your JSON file
INPUT_JSON_FILE = "/Users/kirupa/Documents/projects/agenticai/genAIHackTrial/sample.json"
# This will be the new file in JSON Lines format
OUTPUT_JSON_LINES_FILE = 'output_for_bigquery.jsonl'

# Run the conversion
convert_json_to_json_lines(INPUT_JSON_FILE, OUTPUT_JSON_LINES_FILE)