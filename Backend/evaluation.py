import numpy as np
import pandas as pd
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer
import nltk
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_bleu(reference, prediction):
    """
    Calculate BLEU score for a single prediction.
    
    Args:
        reference (str): The reference/ground truth text
        prediction (str): The predicted text
        
    Returns:
        float: BLEU score
    """
    try:
        # Tokenize the texts
        reference_tokens = nltk.word_tokenize(reference.lower())
        prediction_tokens = nltk.word_tokenize(prediction.lower())
        
        # Calculate BLEU score
        smoothing = SmoothingFunction().method1
        bleu_score = sentence_bleu([reference_tokens], prediction_tokens, smoothing_function=smoothing)
        
        return bleu_score
    except Exception as e:
        logger.warning(f"Error calculating BLEU score: {e}")
        return 0.0

def calculate_rouge(reference, prediction):
    """
    Calculate ROUGE scores for a single prediction.
    
    Args:
        reference (str): The reference/ground truth text
        prediction (str): The predicted text
        
    Returns:
        dict: Dictionary containing ROUGE-1, ROUGE-2, and ROUGE-L scores
    """
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        scores = scorer.score(reference, prediction)
        
        return {
            'rouge1': scores['rouge1'].fmeasure,
            'rouge2': scores['rouge2'].fmeasure,
            'rougeL': scores['rougeL'].fmeasure
        }
    except Exception as e:
        logger.warning(f"Error calculating ROUGE score: {e}")
        return {'rouge1': 0.0, 'rouge2': 0.0, 'rougeL': 0.0}

def calculate_perplexity(model, tokenizer, text):
    """
    Calculate perplexity for a given text using the model.
    
    Args:
        model: The T5 model
        tokenizer: The T5 tokenizer
        text (str): The text to calculate perplexity for
        
    Returns:
        float: Perplexity score
    """
    try:
        # Tokenize the text
        inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        
        # Move to the same device as the model
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Calculate loss
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs['input_ids'])
            loss = outputs.loss
            
        # Calculate perplexity
        perplexity = torch.exp(loss).item()
        
        return perplexity
    except Exception as e:
        logger.warning(f"Error calculating perplexity: {e}")
        return float('inf')

def evaluate_model(model, tokenizer, test_df, sample_number=80):
    """
    Evaluate the model using BLEU, ROUGE, and perplexity metrics.
    
    Args:
        model: The T5 model
        tokenizer: The T5 tokenizer
        test_df (pd.DataFrame): Test dataset with 'question' and 'answer' columns
        sample_number (int): Number of samples to evaluate
        
    Returns:
        dict: Dictionary containing average scores
    """
    bleu_scores = []
    rouge_scores = []
    perplexity_scores = []

    # Sample the test data
    test_df = test_df.sample(n=min(sample_number, len(test_df)), random_state=42)
    logger.info(f"Evaluating on {len(test_df)} samples")

    for idx, row in test_df.iterrows():
        try:
            logger.info(f"Processing sample {idx + 1}/{len(test_df)}")
            
            # Generate prediction
            input_text = f"Answer this irrigation question: {row['question']}"
            inputs = tokenizer.encode(input_text, return_tensors='pt', truncation=True, max_length=256)
            
            # Move to the same device as the model
            device = next(model.parameters()).device
            inputs = inputs.to(device)
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    inputs, 
                    max_length=200,
                    num_beams=4,
                    early_stopping=True,
                    do_sample=True,
                    temperature=0.7
                )
            
            prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt if it appears in the prediction
            if "Answer this irrigation question:" in prediction:
                prediction = prediction.split("Answer this irrigation question:")[-1].strip()
            
            # Calculate metrics
            bleu = calculate_bleu(row['answer'], prediction)
            rouge = calculate_rouge(row['answer'], prediction)
            perplexity = calculate_perplexity(model, tokenizer, row['answer'])

            bleu_scores.append(bleu)
            rouge_scores.append(rouge)
            perplexity_scores.append(perplexity)
            
            logger.info(f"Sample {idx + 1} - BLEU: {bleu:.4f}, ROUGE-1: {rouge['rouge1']:.4f}, Perplexity: {perplexity:.2f}")
            
        except Exception as e:
            logger.error(f"Error processing sample {idx}: {e}")
            continue

    # Filter out infinite perplexities
    valid_perplexities = [p for p in perplexity_scores if p != float('inf')]

    # Calculate average scores
    avg_bleu = np.mean(bleu_scores) if bleu_scores else 0.0
    avg_rouge1 = np.mean([r['rouge1'] for r in rouge_scores]) if rouge_scores else 0.0
    avg_rouge2 = np.mean([r['rouge2'] for r in rouge_scores]) if rouge_scores else 0.0
    avg_rougeL = np.mean([r['rougeL'] for r in rouge_scores]) if rouge_scores else 0.0
    avg_perplexity = np.mean(valid_perplexities) if valid_perplexities else float('inf')

    # Print results
    print(f"\n=== EVALUATION RESULTS ===")
    print(f"Number of samples evaluated: {len(bleu_scores)}")
    print(f"BLEU Score: {avg_bleu:.4f}")
    print(f"ROUGE-1: {avg_rouge1:.4f}")
    print(f"ROUGE-2: {avg_rouge2:.4f}")
    print(f"ROUGE-L: {avg_rougeL:.4f}")
    print(f"Perplexity: {avg_perplexity:.2f}")
    print(f"Valid perplexity samples: {len(valid_perplexities)}/{len(perplexity_scores)}")

    return {
        'bleu': avg_bleu,
        'rouge1': avg_rouge1,
        'rouge2': avg_rouge2,
        'rougeL': avg_rougeL,
        'perplexity': avg_perplexity,
        'num_samples': len(bleu_scores)
    }

def load_model_and_tokenizer(model_path):
    """
    Load the model and tokenizer from the specified path.
    
    Args:
        model_path (str): Path to the model directory
        
    Returns:
        tuple: (model, tokenizer)
    """
    try:
        logger.info(f"Loading model from {model_path}")
        tokenizer = T5Tokenizer.from_pretrained(model_path)
        model = T5ForConditionalGeneration.from_pretrained(model_path, from_tf=True)
        
        # Move to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        
        logger.info(f"Model loaded successfully on {device}")
        return model, tokenizer
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    import os
    
    # Model path
    model_path = os.path.join(os.path.dirname(__file__), "..", "Irrigation_model")
    
    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer(model_path)
    
    # Create sample test data (replace with your actual test data)
    test_data = [
        {
            'question': 'How often should I water my tomato plants?',
            'answer': 'Water tomato plants deeply 2-3 times per week, ensuring the soil is moist but not waterlogged. Adjust frequency based on weather conditions and soil type.'
        },
        {
            'question': 'What is the best time to irrigate crops?',
            'answer': 'The best time to irrigate crops is early morning (before 10 AM) or late evening (after 6 PM) to minimize water loss through evaporation and ensure optimal absorption.'
        },
        {
            'question': 'How do I check if my soil needs watering?',
            'answer': 'Insert your finger 2-3 inches into the soil. If it feels dry, water is needed. For more accurate measurement, use a soil moisture meter or observe plant wilting.'
        }
    ]
    
    test_df = pd.DataFrame(test_data)
    
    # Run evaluation
    results = evaluate_model(model, tokenizer, test_df, sample_number=3)
    
    print(f"\nFinal Results: {results}") 