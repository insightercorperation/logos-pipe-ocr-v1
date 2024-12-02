from .metric import accuracy, cer, wer, cosine_similarity, jaccard_similarity

class TextEvaluator:  
    def __init__(self, metrics: list[str]):
        self.predicted_text = None
        self.ground_truth_text = None
        self.metrics = metrics
        self.metric_result = {}
        self.metric_functions = {
            "accuracy": accuracy,
            "cer": cer,
            "wer": wer,
            "cosine_similarity": cosine_similarity,
            "jaccard_similarity": jaccard_similarity
        }

    def run(self, predicted_text: str | list, ground_truth_text: str | list) -> dict:  
        self.predicted_text = predicted_text
        self.ground_truth_text = ground_truth_text

        if self._check_metric_validity(self.metrics):
            self.metric_result = {metric: 0.0 if metric == "accuracy" else 1.0 for metric in self.metrics}
        
        if not self.predicted_text or not self.ground_truth_text:
            return self._handle_empty_texts()
        
        if self._check_type_validity(self.predicted_text, self.ground_truth_text):
            if isinstance(self.ground_truth_text, bool):
                return None

            if isinstance(self.ground_truth_text, list):
                metric_result_list = {metric: [] for metric in self.metrics}
                if len(self.predicted_text) > len(self.ground_truth_text):
                    raise IndexError("Predicted_text is longer than ground_truth_text.")
                for i, truth_text in enumerate(self.ground_truth_text):
                    if i < len(self.predicted_text):
                        pred_text = self.predicted_text[i]
                        for metric in self.metrics:
                            metric_result_list[metric].append(self.metric_functions[metric](pred_text, truth_text))
                    else:
                        raise IndexError("Predicted_text is shorter than ground_truth_text.")
                return self._average_metric(metric_result_list)
            else:
                for metric in self.metrics:
                    self.metric_result[metric] = self.metric_functions[metric](self.predicted_text, self.ground_truth_text)
                return self.metric_result
        else:
            return None
        
    def _handle_empty_texts(self) -> dict:
        if not self.predicted_text and not self.ground_truth_text:
            return {metric: 1.0 if metric == "accuracy" else 0.0 for metric in self.metrics}
        return self.metric_result
    
    def _check_type_validity(self, predicted_text: str | list, ground_truth_text: str | list) -> bool: # check text validity
        if type(predicted_text) == type(ground_truth_text):
            return True
        else:
            raise ValueError(f"WARNING: Types of predicted_text and ground_truth_text are different. Unable to calculate metrics. predicted_text type: {type(predicted_text)}, ground_truth_text type: {type(ground_truth_text)}")

    def _check_metric_validity(self, metrics: list[str]) -> bool: # check metric validity
        for metric in metrics:
            if metric not in globals():
                raise ValueError(f"Can't calculate metrics. Metric '{metric}' is not valid.")
        return True

    def _average_metric(self, metric_result_list: dict) -> dict: # calculate average metric
        return {metric: sum(value) / len(value) for metric, value in metric_result_list.items()}