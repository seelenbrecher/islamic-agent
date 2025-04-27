import argparse
import json
import nltk

from nltk.translate.bleu_score import corpus_bleu
from rouge import Rouge


def evaluate_qa(data):
    references = []
    predictions = []

    for item in data:
        references.append([item["answer"].split()])  # List of lists of tokens
        predictions.append(item["predicted_answer"].split())

    # BLEU Evaluation
    bleu_score = corpus_bleu(references, predictions)

    # ROUGE Evaluation
    rouge = Rouge()
    rouge_scores = rouge.get_scores(
        [" ".join(pred) for pred in predictions],  # Convert back to strings
        [" ".join(ref[0]) for ref in references],  # Convert back to strings
        avg=True  # Calculate average scores across all examples
    )

    # METEOR Evaluation
    meteor_scores = []
    for i in range(len(references)):
        meteor_scores.append(nltk.translate.meteor_score.single_meteor_score(references[i][0], predictions[i]))
    meteor_score = sum(meteor_scores) / len(meteor_scores) if meteor_scores else 0

    return {
        "bleu": bleu_score,
        "rouge": rouge_scores,
        "meteor": meteor_score,
    }


def main(args):
    data = json.load(open(args.in_file))
    
    results = evaluate_qa(data)
    print("Evaluation Results:")
    print(f"BLEU: {results['bleu']:.4f}")  # Format for readability
    print("ROUGE:")
    for key in results['rouge']:
        value = results['rouge'][key]
        print(f"  {key}: {value}")  # Format for readability
    print(f"METEOR: {results['meteor']:.4f}")
    
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_file')
    parser.add_argument('--out_file')
    args = parser.parse_args()
    main(args)
