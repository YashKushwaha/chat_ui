from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import base64
class ImageEmbedder:
    def __init__(self, model_name):
        #"openai/clip-vit-base-patch32"
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def embed(self, image_paths):
        images = [Image.open(img_path).convert("RGB") for img_path in image_paths]
        inputs = self.processor(images=images, return_tensors="pt", padding=True)
        with torch.no_grad():
            embeddings = self.model.get_image_features(**inputs)
        return embeddings.cpu().numpy()

class LlavaImageEmbedder:
    def __init__(self):
        pass
        #self.model_name = model_name  # optional: store for logging/debugging

    def embed(self, image_path):
        with open(image_path, "rb") as img_file:
            image_b64 = base64.b64encode(img_file.read()).decode("utf-8")
        return image_b64  # or open(image_path, "rb").read() if you prefer

def load_image_embedder(config):
    if config['model_name'] == 'llava':
        return LlavaImageEmbedder()