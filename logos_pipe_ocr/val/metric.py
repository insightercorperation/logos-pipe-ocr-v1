from Levenshtein import distance as levenshtein_distance
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def accuracy(predicted_text: str, ground_truth_text: str) -> float: # 정확도 계산
    correct_predictions = sum(1 for p, g in zip(predicted_text, ground_truth_text) if p == g)
    accuracy = correct_predictions / len(ground_truth_text)
    return min(accuracy, 1.0)

def cer(predicted_text: str, ground_truth_text: str) -> float:  # 문자 오류율(CER) 계산
    edit_distance = levenshtein_distance(predicted_text, ground_truth_text)
    cer = edit_distance / len(ground_truth_text)  # 실제 텍스트 길이로 나누기
    return min(cer, 1.0)

def wer(predicted_text: str, ground_truth_text: str) -> float:  # 단어 오류율(WER) 계산
    predicted_words = predicted_text.split()
    ground_truth_words = ground_truth_text.split()
    edit_distance = levenshtein_distance(' '.join(predicted_words), ' '.join(ground_truth_words))
    wer = edit_distance / len(ground_truth_words)
    return min(wer, 1.0)

def cosine_similarity(predicted_text: str, ground_truth_text: str) -> float: 
    if len(predicted_text.split()) == 1 and len(ground_truth_text.split()) == 1: # if predicted_text와 ground_truth_text가 단어 하나인 경우
        return 1.0 if predicted_text == ground_truth_text else 0.0

    vectorizer = CountVectorizer().fit_transform([predicted_text, ground_truth_text])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return float(cosine_sim[0][1])

def jaccard_similarity(predicted_text: str, ground_truth_text: str) -> float: # 자카드 유사도 계산
    predicted_text_set = set(predicted_text.split())
    ground_truth_text_set = set(ground_truth_text.split())
    
    intersection = len(ground_truth_text_set.intersection(predicted_text_set))
    union = len(ground_truth_text_set.union(predicted_text_set))
    
    if union == 0:  # 합집합이 비어있을 경우
        return 0.0
    return intersection / union

def check_text_validity(predicted_text: str | list, ground_truth_text: str | list) -> bool: # 텍스트 유효성 검사
    try:
        if type(predicted_text) == type(ground_truth_text):
            return True
    except TypeError:
        raise TypeError("WARNING: The types of predicted_text and ground_truth_text are different. Can't calculate metrics.")

def average_metric(metric_result_list: dict) -> dict: # 평균 메트릭 계산
    return {metric: sum(value) / len(value) for metric, value in metric_result_list.items()}

def evaluate_text_detection(predicted_text: str | list, ground_truth_text: str | list, metrics: list[str]) -> dict:  
    metric_result = {metric: 0.0 if metric == "accuracy" else 1.0 for metric in metrics} # initialize metric_result

    def handle_empty_texts() -> dict:
        if not predicted_text and not ground_truth_text:  # predicted_text와 ground_truth_text가 모두 비어있는 경우
            return metric_result
        # 둘 중 하나라도 비어있는 경우
        return metric_result
    
    if not predicted_text or not ground_truth_text: # predicted_text 또는 ground_truth_text가 None인 경우
        return handle_empty_texts()
    
    if check_text_validity(predicted_text, ground_truth_text):
        if isinstance(ground_truth_text, bool): # ground_truth_text가 boolean인 경우
            return None
        
        if isinstance(ground_truth_text, list):  # ground_truth_text가 리스트인 경우
            metric_result_list = {metric: [] for metric in metrics}
            for i, truth_text in enumerate(ground_truth_text):
                if isinstance(predicted_text, list) and i < len(predicted_text):  # predicted_text가 리스트이고 인덱스가 범위 내에 있는지 확인
                    pred_text = predicted_text[i]
                    for metric in metrics:
                        if metric in globals():
                            metric_result_list[metric].append(globals()[metric](pred_text, truth_text))
                        else:
                            raise ValueError(f"Metric '{metric}' is not valid.")
                else: 
                    for metric in metrics:
                        if metric in globals():
                            metric_result_list[metric].append(globals()[metric](predicted_text, truth_text))
                        else:
                            raise ValueError(f"Metric '{metric}' is not valid.")
            return average_metric(metric_result_list)
        else:  # ground_truth_text가 리스트가 아닌 경우
            for metric in metrics:
                if metric in globals():
                    metric_result[metric] = globals()[metric](predicted_text, ground_truth_text)
                else:
                    raise ValueError(f"Metric '{metric}' is not valid.")
            return metric_result
    else:
        return None