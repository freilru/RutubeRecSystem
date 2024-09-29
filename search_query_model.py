from safetensors.torch import load_file
from transformers import BertTokenizer, BertForSequenceClassification
import torch

class SearchQueryRepository:
    def __init__(self, model_path, tokenizer_name, classes):
        self.classes = classes

        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_name)
        self.model = BertForSequenceClassification.from_pretrained(tokenizer_name, num_labels=len(classes))

        weights = load_file(model_path)
        self.model.load_state_dict(weights, strict=False)
        self.model.eval()

    def predict(self, query):
        inputs = self.tokenizer(query, return_tensors="pt", truncation=True, padding=True, max_length=128)

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=-1).item()

        return self.classes[predicted_class_id]