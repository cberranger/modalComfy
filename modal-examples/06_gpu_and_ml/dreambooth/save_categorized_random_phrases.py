import json

def save_categorization_to_json(data, output_file):
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Categorization successfully saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while saving the file: {e}")

if __name__ == "__main__":
    categorized_data = {
        "clothing": [
            "red vest",
            "one-shoulder top",
            "blue skirt",
            "beige bra",
            "white panties",
            "brown bra",
            "white towel over her top",
            "patterned shirt",
            "black lace bra",
            "green skirt",
            "tan tank top",
            "workout attire"
        ],
        "accessories": [
            "headscarf",
            "earrings",
            "necklace",
            "flower pin"
        ],
        "face": [
            "teeth visible",
            "fine facial features",
            "winged eyeliner",
            "heavy eyeliner",
            "blue eyes",
            "eyes are wide open",
            "eyebrows are furrowed"
        ],
        "hair": [
            "straight brown hair",
            "brown hair",
            "green hair",
            "orange hair that is blowing in the wind"
        ],
        "environment": [
            "soft lighting",
            "black background",
            "gold background",
            "body of water",
            "clouds in the sky",
            "tropical"
        ],
        "building": [
            "building",
            "large columns",
            "doorway"
        ],
        "person_description": [
            "side pose",
            "a young blonde woman is standing outside. she has long",
            "a woman is standing in a doorway.",
            "a woman is standing in front of the camera.",
            "a woman is sitting on a red chair.",
            "a woman is standing in front of a body of water.",
            "a woman is standing outside in front of a building."
        ],
        "style": [
            "casual chic",
            "fashionable",
            "cozy ambiance",
            "serene",
            "glamour shot",
            "symmetry",
            "modern style"
        ],
        "objects": [
            "black text",
            "red handle",
            "grey dog"
        ],
        "furniture": [
            "red chair",
            "rows of red chairs"
        ],
        "plants": [
            "green leaves",
            "grass she is standing on is green and brown"
        ],
        "uncategorized": [
            "movie premiere",
            "no tattoos",
            "watermark:",
            "minimalist background",
            "hand on cheek",
            "fantastic beasts"
        ]
    }

    # Note: The full phrases like "a woman is standing..." are kept as is for now.
    # If further breakdown is needed, the categorization logic would need to be more complex.
    save_categorization_to_json(categorized_data, "categorized_random_phrases.json")
