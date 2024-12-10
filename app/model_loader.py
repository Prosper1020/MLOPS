import joblib

def load_model(model_path: str):
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        raise Exception("Model file not found. Please check the path.")