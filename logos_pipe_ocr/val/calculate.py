def calculate_schema_validity(fidelity_results:dict) -> int:
    return 1 if fidelity_results['schema_validity'] else 0

def collect_and_extend_missing_fields(all_missing_fields: list, fidelity_results: dict) -> None:
    missing_fields = fidelity_results.get('missing_fields', [])
    if missing_fields:
        all_missing_fields.extend(missing_fields)

def calculate_boolean_predictions(label: bool, pred: bool, counts: dict) -> None:
    if label:  # 실제 Positive
        if pred:  # 예측도 Positive
            counts["TP"] += 1
        else:  # 예측이 Negative
            counts["FN"] += 1
    else:  # 실제 Negative인 경우
        if pred:  # 예측이 Positive
            counts["FP"] += 1  # FP 카운트 증가

def update_boolean_predictions(boolean_results: dict, boolean_predictions: dict) -> None:
    for key, values in boolean_results.items():
        pred = values.get("pred")
        label = values.get("label")

        if key not in boolean_predictions:  # boolean_predictions 딕셔너리에 key가 없으면 초기화
            boolean_predictions[key] = {"TP": 0, "FN": 0, "FP": 0}  # TP, FN, FP 초기화

        # pred 또는 label이 None인 경우를 처리
        if label is None or pred is None:
            continue  # None인 경우 해당 항목을 건너뜁니다.

        calculate_boolean_predictions(label, pred, boolean_predictions[key])  # 계산 함수 호출

def calculate_overall_boolean_results(boolean_predictions: dict, overall_results: dict) -> None:
    for key, counts in boolean_predictions.items():
        if key not in overall_results["fidelity_validation_results"]["boolean_result"]:  # boolean_result key 초기화
            overall_results["fidelity_validation_results"]["boolean_result"][key] = {"TP": 0, "FN": 0, "FP": 0}
        overall_results["fidelity_validation_results"]["boolean_result"][key]["TP"] += counts["TP"]
        overall_results["fidelity_validation_results"]["boolean_result"][key]["FN"] += counts["FN"]
        overall_results["fidelity_validation_results"]["boolean_result"][key]["FP"] += counts["FP"]
        
def calculate_text_metrics(text_results:dict, tv_results:dict) -> None:
    for key, metrics in text_results.items():
        if key not in tv_results:
            tv_results[key] = {}
        
        for metric_key, value in metrics.items():
            if value is None:  # value가 None인 경우 처리
                continue  # None인 경우 해당 항목을 건너뜁니다.
            if metric_key not in tv_results[key]:
                tv_results[key][metric_key] = []
            tv_results[key][metric_key].append(value)

def calculate_averages(tv_results:dict, count:int) -> None:
    for key, metrics in tv_results.items():
        for metric_key, total in metrics.items():
            if total is None:  # total이 None인 경우 처리
                continue  # None인 경우 해당 항목을 건너뜁니다.
            tv_results[key][metric_key] = total / count if count > 0 else 0  # count가 0일 경우 0으로 설정

def calculate_f1_score(boolean_predictions:dict, final_results:dict) -> None:
    # boolean_recall 키가 없으면 초기화
    if "f1_score" not in final_results["fidelity_validation_results"]:
        final_results["fidelity_validation_results"]["f1_score"] = {}
    
    for key, counts in boolean_predictions.items():
        TP = counts["TP"]
        FN = counts["FN"]
        FP = counts["FP"]
        
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        recall = TP / (TP + FN) if (TP + FN) > 0 else 0
        
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        final_results["fidelity_validation_results"]["f1_score"][f"{key}_f1"] = f1_score

def initialize_metric_key(overall_results: dict, metric_key: str, metric_value_key: str) -> None:
    if metric_key not in overall_results["text_validation_results"]:
        overall_results["text_validation_results"][metric_key] = {}
    if metric_value_key not in overall_results["text_validation_results"][metric_key]:
        overall_results["text_validation_results"][metric_key][metric_value_key] = []  # 평균 계산을 위해 리스트 초기화

def process_text_validation_results(metrics: dict, evaluation_metrics: dict, overall_results: dict, test_name: str) -> None:
    for metric_key, metric_values in metrics["text_validation_results"].items():  # 각 테스트 결과 필드 순회
        if evaluation_metrics.get(metric_key) and test_name in evaluation_metrics[metric_key]:  # optional한 검증 항목이 있으면
            for metric_value_key, metric_value in metric_values.items():  # 각 필드별 검증 항목 순회
                initialize_metric_key(overall_results, metric_key, metric_value_key)  # 초기화 함수 호출
                overall_results["text_validation_results"][metric_key][metric_value_key].append(metric_value)
        else:  # optional한 검증 항목이 없으면
            for metric_value_key, metric_value in metric_values.items():
                initialize_metric_key(overall_results, metric_key, metric_value_key)  # 초기화 함수 호출
                overall_results["text_validation_results"][metric_key][metric_value_key].append(metric_value)


def calculate_testset_average_metrics(operation_results:list[dict]) -> dict:
    final_results = {
        "text_validation_results": {},
        "fidelity_validation_results": {
            "schema_validity_percentage": 0,
            "missing_fields": [],
            "boolean_result": {},
            "f1_score": {}
        },
        "sample_size": 0
    }
    text_avg_results = {}  # 평균 계산을 위한 딕셔너리
    count = len(operation_results)

    # schema_validity 비율 계산
    valid_count = 0
    all_missing_fields = []
    boolean_predictions = {}

    for result in operation_results:
        fidelity_results = result.get("fidelity_validation_results")
        if fidelity_results:
            valid_count += calculate_schema_validity(fidelity_results)
            collect_and_extend_missing_fields(all_missing_fields, fidelity_results)

            boolean_results = fidelity_results.get("boolean_result")
            if boolean_results:  # boolean_result가 빈 딕셔너리가 아닐 때만 처리(null 제외)
                update_boolean_predictions(boolean_results, boolean_predictions)

        text_results = result.get("text_validation_results")
        if text_results:
            calculate_text_metrics(text_results, text_avg_results)

    # 평균 계산
    if count > 0:  # count가 0이 아닐 때만 평균 계산
        calculate_averages(text_avg_results, count)
        final_results["text_validation_results"] = text_avg_results

        # schema_validity 비율 추가
        final_results["fidelity_validation_results"] = {
            "schema_validity_percentage": (valid_count / count) * 100,
            "missing_fields": all_missing_fields,  # 중복 없이 모든 필드 추가
            "boolean_result": boolean_predictions
        }

        # recall 계산
        calculate_f1_score(boolean_predictions, final_results)
        final_results["sample_size"] = count

    return final_results