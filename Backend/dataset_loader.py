from datasets import load_dataset
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_mental_health_dataset():
    """
    Load the mental health QA dataset from Hugging Face Hub.
    
    Note: You need to login first using:
    huggingface-cli login
    
    Or set your token as an environment variable:
    export HUGGING_FACE_HUB_TOKEN=your_token_here
    """
    try:
        logger.info("Loading mental health QA dataset...")
        
        # Load the dataset from Hugging Face Hub
        # This will download and cache the dataset locally
        dataset = load_dataset("Srishmath/mental-health-qa-dataset")
        
        logger.info(f"Dataset loaded successfully!")
        logger.info(f"Dataset structure: {dataset}")
        
        # Access different splits
        train_data = dataset.get('train', None)
        test_data = dataset.get('test', None)
        validation_data = dataset.get('validation', None)
        
        if train_data:
            logger.info(f"Training examples: {len(train_data)}")
            logger.info(f"Sample training data: {train_data[0]}")
        
        if test_data:
            logger.info(f"Test examples: {len(test_data)}")
            logger.info(f"Sample test data: {test_data[0]}")
            
        return dataset
        
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise

def load_dataset_with_authentication():
    """
    Alternative method to load dataset with explicit authentication.
    """
    try:
        # Method 1: Using token directly (not recommended for production)
        # dataset = load_dataset("Srishmath/mental-health-qa-dataset", token="your_token_here")
        
        # Method 2: Using environment variable (recommended)
        # Set HUGGING_FACE_HUB_TOKEN environment variable before running
        dataset = load_dataset("Srishmath/mental-health-qa-dataset")
        
        return dataset
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        logger.info("Make sure you're logged in with: huggingface-cli login")
        raise

def explore_dataset(dataset):
    """
    Explore the loaded dataset structure and content.
    """
    logger.info("Exploring dataset structure...")
    
    # Print dataset info
    print(f"Dataset keys: {list(dataset.keys())}")
    
    # Explore each split
    for split_name, split_data in dataset.items():
        print(f"\n{split_name.upper()} SPLIT:")
        print(f"Number of examples: {len(split_data)}")
        print(f"Features: {split_data.features}")
        
        # Show first few examples
        print(f"First 3 examples:")
        for i, example in enumerate(split_data.select(range(min(3, len(split_data))))):
            print(f"  Example {i+1}:")
            for key, value in example.items():
                print(f"    {key}: {value[:100]}{'...' if len(str(value)) > 100 else ''}")

def filter_dataset_by_topic(dataset, topic_filter=None):
    """
    Filter the dataset by specific topics.
    """
    if topic_filter:
        filtered_dataset = dataset.filter(lambda x: topic_filter.lower() in x['topic'].lower())
        logger.info(f"Filtered dataset has {len(filtered_dataset)} examples for topic '{topic_filter}'")
        return filtered_dataset
    return dataset

if __name__ == "__main__":
    # Example usage
    try:
        # Load the dataset
        dataset = load_mental_health_dataset()
        
        # Explore the dataset
        explore_dataset(dataset)
        
        # Example: Filter by topic
        anxiety_data = filter_dataset_by_topic(dataset, "anxiety")
        
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        print("\nTo fix authentication issues:")
        print("1. Run: huggingface-cli login")
        print("2. Enter your Hugging Face token")
        print("3. Or set HUGGING_FACE_HUB_TOKEN environment variable") 