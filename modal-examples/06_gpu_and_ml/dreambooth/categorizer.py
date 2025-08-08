import json

def categorize_phrases(phrases_text):
    categories = {
        "clothing": ["bra", "shirt", "top", "jacket", "pants", "skirt", "robe", "overalls", "uniform", "jumpsuit", "shorts", "thong", "hat", "kimono", "corset", "vest", "towel", "pajamas", "jersey", "glove", "turtleneck", "dress shirt", "white sleeveless top", "black top", "bow on shirt", "pink and white striped shirt", "fishnet top", "red top", "sleeveless top", "grey tank top", "white t-shirt", "text on t-shirt", "halter top", "loose t-shirt", "unbuttoned shirt", "black tank top", "wide sleeves", "sarong", "blouse", "sportswear", "scrunchie", "black headwear", "red necktie", "striped necktie"],
        "dresses": ["dress", "purple dress", "sparkly dress", "shoulder-length dress", "navy blue dress", "silver dress", "blue dress", "lace dress", "beige dress", "off-shoulder dress", "textured dress", "patterned dress", "wearing a green velvet dress", "sequined dress", "asymmetrical dress", "camouflage dress", "pink sleeveless dress", "black and white dress", "one-shoulder dress"],
        "sweaters": ["sweater", "brown sweater", "textured sweater", "high neckline sweater", "yellow sweater", "black sweater", "mint green sweater", "brown turtleneck sweater", "white sweater"],
        "swimwear": ["bikini", "colorful bikini", "high-cut bikini", "swimsuit", "patterned swimsuit"],
        "underwear": ["underwear", "white underwear", "partially visible bra", "bra", "striped panties", "highleg panties"],
        "accessories": ["necklace", "pendant", "earrings", "purse", "chain", "belt", "bracelet", "tattoo", "hairband", "choker", "ring", "headscarf", "flower pin", "ornate headpiece", "perfume bottle", "headband", "blue scarf", "purple nails", "toenail polish"],
        "environment": ["vehicle", "restaurant", "tunnel", "library", "street", "ship", "water", "field", "mountain", "beach", "train tracks", "carousel", "corn field", "bathroom", "desert", "archway", "forest", "kitchen", "locker room", "lighthouse", "sidewalk", "road", "background", "lighting", "sky", "clouds", "city skyline", "gym", "alley", "horizon"],
        "building": ["window", "building", "wall", "columns", "domes", "brick building", "tall building", "white building", "stone wall", "round window", "doorway"],
        "plants": ["flowers", "trees", "potted plants", "weeds", "bushes", "bamboo trees", "lily pad", "plant", "grass", "leaves", "pink flower", "pink rose"],
        "decorations": ["picture", "painting", "artwork", "ornament", "figurine"],
        "furniture": ["stool", "chair", "couch", "table", "bookshelves", "bed", "armchair", "benches", "booth"],
        "hair": ["hair", "blonde hair", "dark hair", "brown hair", "red hair", "orange hair", "purple hair", "green hair", "wavy hair", "long hair", "short hair", "ponytail", "braided", "highlights", "brunette"],
        "face": ["face", "freckles", "goatee", "eyebrows", "mustache", "bald", "eyebrow piercing", "lips", "teeth", "eyeliner", "nose", "eyes"],
        "person_description": ["looking directly at the camera", "smiling", "frown", "serious expression", "slight smirk", "standing", "sitting", "leaning", "medium skin tone", "big belly", "hood down", "mature male", "crossed legs", "hands on lap", "clenched hand", "hand up", "skinny", "pectoral cleavage"],
        "woman": ["woman", "female"],
        "young_woman": ["young woman"],
        "beautiful_woman": ["beautiful young woman"],
        "young_girl": ["young girl"],
        "girl": ["girl"],
        "man": ["man"],
        "old_man": ["old man", "elderly woman"],
        "style": ["casual chic", "modern style", "glamour shot", "refined", "simple composition"],
        "objects": ["motorcycle", "vehicle", "boat", "text", "handle", "dog", "brush", "candle", "spikes", "ceiling light", "drinking glass", "handgun", "mushroom", "sign", "fountain", "aquarium"],
        "themes_concepts": ["high contrast", "high-resolution", "historical", "world war ii", "fresh", "no tattoos", "no makeup", "no jewelry", "no piercings", "no scars", "no watermark", "watermark", "centered subject", "symmetry", "minimalist background", "patreon username", "strap slip", "open fly", "military", "moon", "full moon", "sun", "close-up", "autumn", "photograph", "black and white", "leading lines", "rule of thirds", "symmetrical composition", "soft focus", "fine details"]
    }

    categorized_data = {"uncategorized": []}
    for category in categories:
        categorized_data[category] = []

    phrases = [p.strip() for p in phrases_text.split(', ')] # Split by comma and space

    categorized_data = {"uncategorized": []}
    for category in categories:
        categorized_data[category] = []

    phrases = [p.strip() for p in phrases_text.split(',')] # Split by comma and space

    for phrase in phrases:
        found_category = False
        for category, keywords in categories.items():
            if any(keyword in phrase.lower() for keyword in keywords):
                categorized_data[category].append(phrase)
                found_category = True
                break
        if not found_category:
            categorized_data["uncategorized"].append(phrase)

    return categorized_data

if __name__ == "__main__":
    file_path = "phrases.txt"
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        result = categorize_phrases(content)
        
        output_file = "categorized_phrases.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=4)
        
        print(f"Categorization complete. Results saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
