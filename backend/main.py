"""
End-to-end ABSA pipeline: headline → entity extraction (NER) → sentiment per entity (ABSA).
"""

from pathlib import Path
import numpy as np
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    AutoModelForSequenceClassification,
)

MODEL_DIR = Path(__file__).parent / "models"

NER_ID2LABEL  = {0: "O", 1: "B-ENT", 2: "I-ENT"}
ABSA_ID2LABEL = {0: "negative", 1: "neutral", 2: "positive"}


class ABSAPipeline:
    def __init__(self, device: str | None = None):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        ner_path = MODEL_DIR / "ner_bert_base_cased"
        self.ner_tokenizer = AutoTokenizer.from_pretrained(ner_path)
        self.ner_model = (
            AutoModelForTokenClassification.from_pretrained(ner_path).to(device).eval()
        )

        absa_path = MODEL_DIR / "absa_bert_base_uncased"
        self.absa_tokenizer = AutoTokenizer.from_pretrained(absa_path)
        self.absa_model = (
            AutoModelForSequenceClassification.from_pretrained(absa_path).to(device).eval()
        )

    # NER
    def extract_entities(self, headline: str) -> list[str]:
        words = headline.split()
        enc = self.ner_tokenizer(
            words,
            is_split_into_words=True,
            return_tensors="pt",
            truncation=True,
            max_length=128,
        ).to(self.device)

        with torch.no_grad():
            logits = self.ner_model(**enc).logits  # (1, seq_len, 3)

        pred_ids = logits[0].argmax(-1).cpu().tolist()
        word_ids = enc.word_ids(batch_index=0)

        # Keep only the first subword prediction per word
        word_tags: dict[int, str] = {}
        for tok_idx, wid in enumerate(word_ids):
            if wid is not None and wid not in word_tags:
                word_tags[wid] = NER_ID2LABEL[pred_ids[tok_idx]]

        # Decode BIO spans → entity strings
        entities: list[str] = []
        current: list[str] = []
        for wid in sorted(word_tags):
            tag = word_tags[wid]
            if tag == "B-ENT":
                if current:
                    entities.append(" ".join(current))
                current = [words[wid]]
            elif tag == "I-ENT" and current:
                current.append(words[wid])
            else:
                if current:
                    entities.append(" ".join(current))
                    current = []
        if current:
            entities.append(" ".join(current))

        return entities

    # ABSA
    def classify_sentiment(self, headline: str, entity: str) -> dict:
        enc = self.absa_tokenizer(
            headline,
            entity,
            return_tensors="pt",
            truncation=True,
            max_length=128,
        ).to(self.device)

        with torch.no_grad():
            logits = self.absa_model(**enc).logits  # (1, 3)

        probs = torch.softmax(logits[0], dim=-1).cpu().tolist()
        pred_id = int(np.argmax(probs))

        return {
            "sentiment": ABSA_ID2LABEL[pred_id],
            "confidence": round(probs[pred_id], 4),
            "scores": {ABSA_ID2LABEL[i]: round(p, 4) for i, p in enumerate(probs)},
        }

    # Full pipeline
    def analyze(self, headline: str) -> dict:
        """Return sentiment for every entity detected in the headline."""
        entities = self.extract_entities(headline)
        results = [
            {"entity": ent, **self.classify_sentiment(headline, ent)}
            for ent in entities
        ]
        return {"headline": headline, "entities": results}

    def analyze_batch(self, headlines: list[str]) -> list[dict]:
        return [self.analyze(h) for h in headlines]

# Quick demo
if __name__ == "__main__":
    pipe = ABSAPipeline()
    print(f"Device: {pipe.device}\n")

    samples = [
        "YES Bank shares surge after RBI clears rescue plan",
        "Infosys Q3 profit falls short of estimates; TCS reports record earnings",
        "Trade long on infrastructure stocks: Devang Visaria",
        "MMTC is bad",
    ]

    for headline in samples:
        result = pipe.analyze(headline)
        print(f"Headline : {result['headline']}")
        if result["entities"]:
            for e in result["entities"]:
                print(f"  [{e['sentiment']:8s} {e['confidence']:.2f}]  {e['entity']}")
        else:
            print("  (no entities detected)")
        print()
