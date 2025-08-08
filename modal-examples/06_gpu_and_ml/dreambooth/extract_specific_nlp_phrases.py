import json
import random

def extract_specific_nlp_phrases(input_file, output_file, start_line, num_lines=50):
    try:
        with open(input_file, 'r') as f:
            categorized_data = json.load(f)
        
        all_phrases = []
        for category, phrases in categorized_data.items():
            all_phrases.extend(phrases)
        
        # Remove duplicates while preserving order
        all_phrases = list(dict.fromkeys(all_phrases))

        # Filter phrases from the specified start_line onwards
        # This is an approximation as JSON lines don't directly map to phrase indices
        # We'll take phrases from the list starting at the given index.
        # Adjusting for 0-based indexing
        filtered_phrases = all_phrases[start_line - 1:]

        if len(filtered_phrases) < num_lines:
            print(f"Warning: Not enough phrases ({len(filtered_phrases)}) from line {start_line} onwards to select {num_lines}. Selecting all available phrases.")
            selected_phrases = filtered_phrases
        else:
            selected_phrases = random.sample(filtered_phrases, num_lines)
        
        with open(output_file, 'w') as f:
            for phrase in selected_phrases:
                f.write(phrase + '\n')
        
        print(f"Successfully extracted {len(selected_phrases)} phrases to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_nlp_file = "nlp_categorized_phrases.json"
    output_random_nlp_file = "random_nlp_phrases_from_895.txt"
    start_line_number = 895
    extract_specific_nlp_phrases(input_nlp_file, output_random_nlp_file, start_line_number)
