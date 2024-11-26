from Levenshtein import distance as levenshtein_distance
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def evaluate_levenshtein(predicted_text: str, ground_truth_text: str) -> float: # Levenshtein 거리 계산(편집거리 계산)    
    edit_distance = levenshtein_distance(predicted_text, ground_truth_text)
    accuracy = 1 - (edit_distance / max(len(predicted_text), len(ground_truth_text)))
    return accuracy

def evaluate_accuracy(predicted_text: str, ground_truth_text: str) -> float: # 정확도 계산
    correct_predictions = sum(1 for p, g in zip(predicted_text, ground_truth_text) if p == g)
    accuracy = correct_predictions / max(len(predicted_text), len(ground_truth_text), 1)  # 두 텍스트의 길이 중 최대값으로 나누기
    return accuracy

def calculate_cer(predicted_text: str, ground_truth_text: str) -> float:  # 문자 오류율(CER) 계산
    edit_distance = levenshtein_distance(predicted_text, ground_truth_text)
    cer = edit_distance / len(ground_truth_text)  # 실제 텍스트 길이로 나누기
    return min(cer, 1.0)# 1 초과 시 1로 제한

def calculate_wer(predicted_text: str, ground_truth_text: str) -> float:  # 단어 오류율(WER) 계산
    predicted_words = predicted_text.split()
    ground_truth_words = ground_truth_text.split()
    edit_distance = levenshtein_distance(' '.join(predicted_words), ' '.join(ground_truth_words))
    return edit_distance / max(len(ground_truth_words), 1)  # 실제 단어 수로 나누기

def evaluate_cosine_similarity(predicted_text: str, ground_truth_text: str) -> float: # 코사인 유사도 계산
    # 단어가 하나인 경우에도 처리
    if len(predicted_text.split()) == 1 and len(ground_truth_text.split()) == 1:
        return 1.0 if predicted_text == ground_truth_text else 0.0

    vectorizer = CountVectorizer().fit_transform([predicted_text, ground_truth_text])
    vectors = vectorizer.toarray()
    cosine_sim = cosine_similarity(vectors)
    return float(cosine_sim[0][1])  # 두 텍스트 간의 유사도 반환

def evaluate_jaccard_similarity(predicted_text: str, ground_truth_text: str) -> float: # 자카드 유사도 계산
    predicted_text_set = set(predicted_text.split())
    ground_truth_text_set = set(ground_truth_text.split())
    
    intersection = len(ground_truth_text_set.intersection(predicted_text_set))
    union = len(ground_truth_text_set.union(predicted_text_set))
    
    if union == 0:  # 합집합이 비어있을 경우
        return 0.0
    return intersection / union

def set_metric_result(metric_result: dict) -> dict: # 메트릭 결과 설정
    metric_result = {"accuracy": 0.0, "cer": 0.0, "wer": 0.0, "cosine": 0.0, "jaccard": 0.0}
    return metric_result

def calculate_average_metric(metric_result: dict) -> dict: # 평균 메트릭 계산
    return {key: sum(value) / len(value) for key, value in metric_result.items()}

def 

def evaluate_text_detection(predicted_text: str | list, ground_truth_text: str | list) -> dict:  
    metric_result = {"accuracy": 0.0, "cer": 0.0, "wer": 0.0, "cosine": 0.0, "jaccard": 0.0}
    
    def handle_empty_texts() -> dict:
        if not predicted_text and not ground_truth_text:  # predicted_text와 ground_truth_text가 모두 비어있는 경우
            return metric_result
        # 둘 중 하나라도 비어있는 경우
        return metric_result

    if isinstance(ground_truth_text, bool): # ground_truth_text가 boolean인 경우
        return None
    
    if not predicted_text or not ground_truth_text: # predicted_text 또는 ground_truth_text가 None인 경우
        return handle_empty_texts()
    
    if isinstance(ground_truth_text, list):  # ground_truth_text가 리스트인 경우
        cer_list = []
        for i, truth_text in enumerate(ground_truth_text):
            if isinstance(predicted_text, list) and i < len(predicted_text):  # predicted_text가 리스트이고 인덱스가 범위 내에 있는지 확인
                pred_text = predicted_text[i]
                accuracy = evaluate_accuracy(pred_text, truth_text)
                cer = calculate_cer(pred_text, truth_text)
                wer = calculate_wer(pred_text, truth_text)
                cosine = evaluate_cosine_similarity(pred_text, truth_text)
                jaccard = evaluate_jaccard_similarity(pred_text, truth_text)
                
            else: # predicted_text가 리스트가 아니거나 인덱스가 범위를 초과할 경우
                metric_result["cer"] = 1.0 # 문자 오류율(CER) 1.0으로 설정
            cer_list.append(metric_result["cer"])
        metric_result["cer"] = sum(cer_list) / len(cer_list) # 평균 문자 오류율(CER) 계산
        return metric_result
    else:  # ground_truth_text가 리스트가 아닌 경우
        cer = calculate_cer(predicted_text, ground_truth_text)
        return { "cer": cer }