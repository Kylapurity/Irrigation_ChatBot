from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import re
import logging
import os

# Initialize FastAPI app
app = FastAPI()

# Enable CORS to allow communication with your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the model path (FIXED: Consistent variable name)
MODEL_PATH = r"C:\Users\Kyla\Downloads\Irrigation_model"  # Path to model directory

# Load the model and tokenizer (FIXED: Added from_tf=True for TensorFlow weights)
tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH, from_tf=True)  # Critical fix

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Text cleaning function
def clean_text(text):
    """
    Clean the user input by removing unnecessary phrases, special characters, and normalizing whitespace.
    """
    text = str(text) if text is not None else ''
    text = re.sub(r'Hey\s+[A-Za-z]+\s*[!|,]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[A-Za-z]+,\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b[A-Za-z]+\s*(?=[.!?])', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bHey\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Define the input model using Pydantic
class Query(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)

# Define the prediction endpoint
@app.post("/predict/")
async def predict(query: Query):
    """
    Generate an irrigation advice response based on the user's query.
    """
    try:
        # Log the received question
        logger.info(f"Received question: {query.question}")

        # Clean the input query
        cleaned_query = clean_text(query.question)

        # Tokenize the cleaned query for T5
        input_ids = tokenizer(
            f"generate irrigation advice: {cleaned_query}",
            return_tensors="pt",
            max_length=128,
            truncation=True
        ).input_ids.to(device)

        # Generate response using the T5 model
        outputs = model.generate(
            input_ids,
            max_length=128,
            num_beams=5,
            early_stopping=True
        )

        # Decode the generated response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Log the generated response
        logger.info(f"Generated response: {response}")

        # Return the response as JSON
        return {"response": response}

    except Exception as e:
        # Log any errors and raise an HTTP exception
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))