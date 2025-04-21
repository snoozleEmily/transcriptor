MODELS = [
        "tiny",    # 0 -> Fastest, lowest accuracy
        "base",    # 1 -> Fast, low accuracy
        "small",   # 2 -> Medium speed, medium accuracy
        "medium",  # 3 -> Medium speed, high accuracy
        "large"    # 4 -> Slowest, highest accuracy
        ]

# Model speed profiles (words per second approximation)
MODEL_SPEEDS = {
    'tiny': 30,  
    'base': 20,
    'small': 15,
    'medium': 5,
    'large': 2    
}

# Setup times for complex models (seconds)
SETUP_TIMES = {
    'medium': 22,
    'large': 32
}