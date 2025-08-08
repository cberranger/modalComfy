import json
from sentence_transformers import SentenceTransformer, util

def nlp_categorize_phrases(
    phrases_file="phrases.txt",
    random_phrases_file="random_phrases.txt",
    categorized_random_phrases_file="categorized_random_phrases.json",
    output_file="nlp_categorized_phrases.json",
    similarity_threshold=0.5
):
    try:
        # Load the SentenceTransformer model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # 1. Read all phrases from phrases.txt
        with open(phrases_file, 'r') as f:
            content = f.read()
        all_phrases = [p.strip() for p in content.split(', ')]
        all_phrases = [phrase for phrase in all_phrases if phrase] # Filter out empty strings

        # 2. Read random phrases and their categories
        with open(random_phrases_file, 'r') as f:
            random_phrases_list = [p.strip() for p in f.readlines()]
            random_phrases_list = [phrase for phrase in random_phrases_list if phrase]

        with open(categorized_random_phrases_file, 'r') as f:
            categorized_random_data = json.load(f)
        
        # Create a mapping from random phrase to its category
        random_phrase_to_category = {}
        for category, phrases in categorized_random_data.items():
            for phrase in phrases:
                # For full phrases, we need to handle them carefully.
                # If the phrase is a full sentence, use it as is.
                # Otherwise, it's a keyword.
                if phrase in random_phrases_list:
                    random_phrase_to_category[phrase] = category
                else:
                    # For sub-phrases like "long brown hair" from a longer sentence
                    # This part might need refinement based on how 'categorized_random_phrases.json' was built
                    # For now, let's assume the keys in categorized_random_data are the exact phrases from random_phrases.txt
                    # if not, we'd need to iterate through all_phrases to find the exact match
                    pass

        # Generate embeddings for all phrases
        all_phrase_embeddings = model.encode(all_phrases, convert_to_tensor=True)
        random_phrase_embeddings = model.encode(random_phrases_list, convert_to_tensor=True)

        nlp_categorized_results = {category: [] for category in categorized_random_data.keys()}
        nlp_categorized_results["uncategorized"] = []
        if "uncategorized_nlp" not in nlp_categorized_results:
            nlp_categorized_results["uncategorized_nlp"] = []

        # Keep track of phrases that have been categorized
        categorized_phrases_set = set()

        # Perform similarity search
        for i, random_phrase in enumerate(random_phrases_list):
            category_of_random_phrase = random_phrase_to_category.get(random_phrase, "uncategorized_nlp")
            
            # Calculate cosine similarities
            cosine_scores = util.cos_sim(random_phrase_embeddings[i], all_phrase_embeddings)[0]

            # Find matches above threshold
            for j, score in enumerate(cosine_scores):
                if score.item() >= similarity_threshold:
                    phrase_to_categorize = all_phrases[j]
                    if phrase_to_categorize not in categorized_phrases_set:
                        nlp_categorized_results[category_of_random_phrase].append(phrase_to_categorize)
                        categorized_phrases_set.add(phrase_to_categorize)

        # Add any remaining uncategorized phrases
        for phrase in all_phrases:
            if phrase not in categorized_phrases_set:
                nlp_categorized_results["uncategorized"].append(phrase)

        # Save results
        with open(output_file, 'w') as f:
            json.dump(nlp_categorized_results, f, indent=4)
        print(f"NLP categorization complete. Results saved to {output_file}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    nlp_categorize_phrases()
