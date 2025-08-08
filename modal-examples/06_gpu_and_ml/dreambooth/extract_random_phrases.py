import random

def extract_random_phrases(input_file, output_file, num_lines=40):
    try:
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Assuming phrases are separated by ', ' as observed before
        phrases = [p.strip() for p in content.split(', ')]
        
        # Filter out empty strings that might result from splitting
        phrases = [phrase for phrase in phrases if phrase]

        if len(phrases) < num_lines:
            print(f"Warning: Not enough phrases ({len(phrases)}) in the input file to select {num_lines}. Selecting all available phrases.")
            selected_phrases = phrases
        else:
            selected_phrases = random.sample(phrases, num_lines)
        
        with open(output_file, 'w') as f:
            for phrase in selected_phrases:
                f.write(phrase + '\n')
        
        print(f"Successfully extracted {len(selected_phrases)} phrases to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_phrases_file = "phrases.txt"
    output_random_file = "random_phrases.txt"
    extract_random_phrases(input_phrases_file, output_random_file)
