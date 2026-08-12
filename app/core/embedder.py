import logging

import torch
from sentence_transformers import SentenceTransformer


def load_model(model_name: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"Loading model: {model_name} for device: {device}")
    return SentenceTransformer(model_name, device=device)


def embed(texts: list[str], model: SentenceTransformer) -> list[list[float]]:
    logging.debug(f"Embedding chunks using model: {model}")
    # validate first
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            raise ValueError(f"Expected string at index {i}, got {type(text)}")

    encoded_text = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return encoded_text.tolist()


def embed_one(text: str, model: SentenceTransformer, prompt_name: str | None) -> list[float]:
    model.encode(text, prompt_name=prompt_name)
    result = embed([text], model)
    return result[0]
