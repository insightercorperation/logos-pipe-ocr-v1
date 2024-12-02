import argparse

from logos_pipe_ocr.val.evaluation import Evaluation

def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--label-path", type=str, required=True, help="Label path(directory or file)")
    parser.add_argument("--output-path", type=str, required=True, help="Output path(directory or file)")
    parser.add_argument("--eval-metrics", type=str, nargs='+', required=False, help="Evaluation metrics (default: accuracy, cer, wer, cosine_similarity, jaccard_similarity)", default=["accuracy", "cer", "wer", "cosine_similarity", "jaccard_similarity"])

def main(label_path: str, output_path: str, eval_metrics: str):
    # load the model and run the model
    quality_assessment = Evaluation(label_path, output_path, eval_metrics)
    quality_assessment.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="logos-pipe-ocr: Quality Assessment CLI")
    add_arguments(parser)
    args = parser.parse_args()
    main(args.label_path, args.output_path, args.eval_metrics)
