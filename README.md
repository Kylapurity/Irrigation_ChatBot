# Shamba IrrigationBot – AI Chatbot for Irrigation Support in Kenya

*Shamba IrrigationBot* is an artificial intelligence-powered chatbot designed to assist Kenyan smallholder farmers by providing timely and accurate irrigation advice. The chatbot addresses water management challenges, promotes better crop yields, and supports food security by sharing expert knowledge through an intuitive web interface.

## Project Overview

This project fine-tunes the T5-base model on a curated Water Irrigation Dataset to generate dynamic, context-aware responses to farmers’ questions. The chatbot is lightweight and accessible through a browser, making it practical for farmers in rural areas with limited internet connectivity.

## Dataset

The dataset used was obtained from Hugging Face and contains 3,851 entries. Each entry includes:

- *QUESTION.question*: A farmer's query (e.g., "How do I irrigate maize?")
- *ANSWER*: An expert response (e.g., "Use drip irrigation to conserve water and ensure even moisture distribution.")

The dataset covers:
- Crop-specific irrigation
- Drip systems
- Water technology and pipe selection
- Irrigation methods for yield improvement

## Data Preprocessing

To prepare the dataset for training with the T5-base model (220M parameters), the following steps were applied:

- *Dataset Split*: 80% training, 10% validation, 10% test
- *Text Normalisation*: Lowercased text, removed extra spaces and special characters
- *Tokenization*: Used T5-base tokenizer with a maximum sequence length of 128 tokens
- *Input Format*: "generate irrigation advice: [query]"
- *Quality Checks*: Removed duplicates, ensured query diversity
- *Monitoring*: Used Weights & Biases (wandb.ai) to track training and hyperparameter performance

## Model Training

The T5-base model was selected for its ability to generate natural language responses with moderate computational demands, making it ideal for use in limited-resource environments.

### Fine-Tuning Details

| Parameter           | Value                    |
|---------------------|--------------------------|
| Epochs              | 25                       |
| Batch Size          | 8 (training), 16 (eval)  |
| Optimizer           | Adam                     |
| Learning Rate       | 2e-5 (best result)       |
| Max Sequence Length | 128 tokens               |
| Padding & Truncation| Applied to all samples   |

## Hyperparameter Experiments

Ten experiments were conducted to tune performance. Below is a summary of the results:

| Experiment | Model    | Optimizer | Batch Size | Learning Rate | Max Length | Padding | BLEU | F1   | ROUGE | Epochs |
|------------|----------|-----------|------------|----------------|------------|---------|------|------|--------|--------|
| 1          | T5-base  | Adam      | 10         | 2e-5           | 512        | Max     | 0.40 | 0.31 | 0.35   | 40     |
| 2          | T5-small | Nadam     | 5          | 4e-5           | 256        | Max     | 0.25 | 0.46 | 0.30   | 30     |
| 3          | T5-small | Nadam     | 16         | 1e-5           | 512        | Max     | 0.48 | 0.58 | 0.54   | 20     |
| 4          | T5-base  | Adam      | 8          | 3e-5           | 128        | Max     | 0.23 | 0.49 | 0.45   | 25     |
| 5          | T5-base  | Adam      | 4          | 2e-5           | 128        | Max     | 0.10 | 0.44 | 0.39   | 15     |
| 6          | T5-small | Nadam     | 8          | 4e-5           | 256        | Max     | 0.23 | 0.67 | 0.53   | 10     |
| 7          | T5-small | Nadam     | 4          | 3e-5           | 512        | Max     | 0.43 | 0.45 | 0.60   | 5      |
| 8          | T5-base  | Adam      | 16         | 2e-5           | 128        | Max     | 0.23 | 0.45 | 0.32   | 5      |
| 9          | T5-small | Adam      | 8          | 6e-5           | 512        | Max     | 0.45 | 0.57 | 0.53   | 45     |
| 10         | T5-base  | Nadam     | 8          | 4e-5           | 256        | Max     | 0.11 | 0.33 | 0.48   | 20     |

### Qualitative Testing

Example responses from the chatbot:

| Farmer Question                                   | Chatbot Response                                                                 |
|---------------------------------------------------|----------------------------------------------------------------------------------|
| How do I irrigate maize?                          | For maize, drip irrigation is recommended to conserve water and ensure even distribution. |
| What’s the best way to conserve water for farming?| Use mulching and rainwater harvesting to reduce evaporation and maximise efficiency. |
| Why is training important for biogas technology?  | Proper training ensures operators can maintain biogas systems efficiently and safely. |

## Web App Integration

The chatbot is available through a simple web interface built with React and Tailwind CSS. It includes two user-friendly components:

1. *General Query Box* – for short, everyday irrigation questions  
2. *Detailed Prompt Box* – for more technical or comprehensive irrigation inquiries  

This dual-approach makes it accessible for both novice and experienced users.

## Deployment

- *Frontend*: React + Tailwind CSS  
- *Backend*: Hugging Face Transformers (T5-base)  
- *Deployment Platform*: Vercel  

## Run the Model

To run Shamba IrrigationBot locally, follow the steps below:

### Prerequisites

Ensure the following are installed:

- Python 3.8+  
- pip  
- Node.js and npm  
- Git  

### Backend Setup

1. **Clone the repository**

```bash
git clone https://github.com/Kylapurity/Irrigation_ChatBot.git
cd Irrigation_ChatBot
````

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate       # For Windows: venv\Scripts\activate
```

3. **Install backend dependencies**

```bash
cd Backend\ & Notebook
pip install -r requirements.txt
```

4. **Run the backend server**

```bash
python irrigation_bot_api.py
```

This will start the T5 model-based backend that handles farmer queries.

### Frontend Setup

1. **Navigate to the frontend directory**

```bash
cd ../Frontend_IrrigationBot
```

2. **Install frontend dependencies**

```bash
npm install
```

3. **Start the frontend**

```bash
npm run dev
```


## Challenges and Lessons

* Initially used an unrelated dataset, which led to poor results; switched to a domain-specific irrigation dataset.
* Required extensive text normalization to clean inconsistencies.
* Faced resource limits on Google Colab, which ruled out T5-large due to GPU crashes.
* Learned that smaller models like T5-small often performed better in resource-constrained environments but sometimes at the cost of coherence.

## Conclusion

This project demonstrates that with the right dataset, preprocessing, and training strategy, it is possible to build a practical AI tool to support small-scale farmers. The Shamba IrrigationBot offers a scalable, easy-to-use solution that can significantly enhance agricultural productivity in rural settings.

## Example conversation With Shamba Bot

![Screenshot (1010)](https://github.com/user-attachments/assets/b20c1767-0afa-40e5-88d6-001e54dd7074)
![Screenshot (1012)](https://github.com/user-attachments/assets/01967b73-12a1-4614-bcdf-44706ff07847)

## Demo Video
https://youtu.be/mUbU4yOqQ7o

