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

def check_text_validity(predicted_text: str | list, ground_truth_text: str | list) -> bool: # check text validity
    if type(predicted_text) == type(ground_truth_text):
        return True
    else:
        raise ValueError(f"WARNING: Types of predicted_text and ground_truth_text are different. Unable to calculate metrics. predicted_text type: {type(predicted_text)}, ground_truth_text type: {type(ground_truth_text)}")

def check_metric_validity(metrics: list[str]) -> bool: # check metric validity
    for metric in metrics:
        if metric not in globals():
            raise ValueError(f"Can't calculate metrics. Metric '{metric}' is not valid.")
    return True

def average_metric(metric_result_list: dict) -> dict: # calculate average metric
    return {metric: sum(value) / len(value) for metric, value in metric_result_list.items()}

def evaluate_text_detection(predicted_text: str | list, ground_truth_text: str | list, metrics: list[str]) -> dict:  
    def _handle_empty_texts() -> dict:
        if not predicted_text and not ground_truth_text:  # if predicted_text and ground_truth_text are empty
            return {metric: 1.0 if metric == "accuracy" else 0.0 for metric in metrics}
        # if one of them is empty
        return metric_result
    
    if check_metric_validity(metrics):
        metric_result = {metric: 0.0 if metric == "accuracy" else 1.0 for metric in metrics} # initialize metric_result
    
    if not predicted_text or not ground_truth_text: # if predicted_text or ground_truth_text is None
        return _handle_empty_texts()
    
    if check_text_validity(predicted_text, ground_truth_text):
        if isinstance(ground_truth_text, bool): # if ground_truth_text is boolean
            return None

        if isinstance(ground_truth_text, list):  # if ground_truth_text is list
            metric_result_list = {metric: [] for metric in metrics}
            if len(predicted_text) > len(ground_truth_text): # if predicted_text is longer than ground_truth_text
                raise IndexError("Predicted_text is longer than ground_truth_text. Please check the predicted_text and ground_truth_text.")
            for i, truth_text in enumerate(ground_truth_text):
                if i < len(predicted_text):  # check if predicted_text index is in range    
                    pred_text = predicted_text[i]
                    for metric in metrics:
                        metric_result_list[metric].append(globals()[metric](pred_text, truth_text))
                else: # if predicted_text is shorter than ground_truth_text
                    raise IndexError("Predicted_text is shorter than ground_truth_text. Please check the predicted_text and ground_truth_text.")
            return average_metric(metric_result_list)
        else:  # if ground_truth_text is not list
            for metric in metrics:
                metric_result[metric] = globals()[metric](predicted_text, ground_truth_text)
            return metric_result
    else:
        return None