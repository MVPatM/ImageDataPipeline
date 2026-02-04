from transformers import pipeline

class AIService:
    def __init__(self):
        print("Loading AI vs Real Image Detection model...")
        self.pipe = pipeline("image-classification", model="dima806/ai_vs_real_image_detection")
        print("Model loaded successfully.")

    def predict(self, image):
        try:
            results = self.pipe(image)
            # Find the result with the highest score
            top_result = max(results, key=lambda x: x['score'])
            return top_result
        except Exception as e:
            print(f"Error during AI prediction: {e}")
            return None
