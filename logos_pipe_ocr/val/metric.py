from Levenshtein import distance as levenshtein_distance
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def accuracy(predicted_text: str, ground_truth_text: str) -> float: # calculate accuracy
    correct_predictions = sum(1 for p, g in zip(predicted_text, ground_truth_text) if p == g)
    accuracy = correct_predictions / len(ground_truth_text)
    return min(accuracy, 1.0)

def cer(predicted_text: str, ground_truth_text: str) -> float:  # calculate CER
    edit_distance = levenshtein_distance(predicted_text, ground_truth_text)
    cer = edit_distance / len(ground_truth_text)  # divide by actual text length
    return min(cer, 1.0)

def wer(predicted_text: str, ground_truth_text: str) -> float:  # calculate WER
    predicted_words = predicted_text.split()
    ground_truth_words = ground_truth_text.split()
    edit_distance = levenshtein_distance(' '.join(predicted_words), ' '.join(ground_truth_words))
    wer = edit_distance / len(ground_truth_words)
    return min(wer, 1.0)

def cosine_similarity(predicted_text: str, ground_truth_text: str) -> float: 
    if len(predicted_text.split()) == 1 and len(ground_truth_text.split()) == 1: # if predicted_text and ground_truth_text are single words
        return 1.0 if predicted_text == ground_truth_text else 0.0

    vectorizer = CountVectorizer().fit_transform([predicted_text, ground_truth_text])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return float(cosine_sim[0][1])

def jaccard_similarity(predicted_text: str, ground_truth_text: str) -> float: # calculate Jaccard similarity
    predicted_text_set = set(predicted_text.split())
    ground_truth_text_set = set(ground_truth_text.split())
    
    intersection = len(ground_truth_text_set.intersection(predicted_text_set))
    union = len(ground_truth_text_set.union(predicted_text_set))
    
    if union == 0:  # if union is empty, return 0.0
        return 0.0
    return intersection / union