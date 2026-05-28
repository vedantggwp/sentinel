from __future__ import annotations

from dataclasses import dataclass


MODEL_ID = "Thrad/thrad-distilbert-conversation-classifier"
MODEL_REVISION = "9e7eeadcf69c3f9d286729bb8b6a4f88f7e4faa2"
TOKENIZER_ID = "distilbert-base-uncased"
MAX_LENGTH = 512


@dataclass(frozen=True)
class IntentCategory:
    code: str
    name: str
    description: str


@dataclass(frozen=True)
class IntentPrediction:
    label: str
    label_name: str
    confidence: float
    model_id: str
    model_revision: str


INTENT_CATEGORIES: tuple[IntentCategory, ...] = (
    IntentCategory("A", "academic_help", "Homework, tests, studying, or assignments."),
    IntentCategory(
        "B",
        "personal_writing_or_communication",
        "Emails, messages, posts, letters, or workplace communication.",
    ),
    IntentCategory(
        "C",
        "writing_and_editing",
        "Nonfiction or instructional writing and editing.",
    ),
    IntentCategory(
        "D",
        "creative_writing_and_role_play",
        "Poems, stories, scripts, dialogues, or character roleplay.",
    ),
    IntentCategory(
        "E",
        "general_guidance_and_info",
        "Practical advice, step-by-step guidance, or factual information.",
    ),
    IntentCategory(
        "F",
        "programming_and_data_analysis",
        "Code, debugging, programming tools, or data analysis.",
    ),
    IntentCategory(
        "G",
        "creative_ideation",
        "Brainstorming, concepts, or topic discovery.",
    ),
    IntentCategory("H", "purchasable_products", "Products, services, or prices."),
    IntentCategory("I", "greetings_and_chitchat", "Small talk or casual chat."),
    IntentCategory(
        "J",
        "relationships_and_personal_reflection",
        "Emotions, relationships, or introspection.",
    ),
    IntentCategory(
        "K",
        "media_generation_or_analysis",
        "Visual, audio, or media creation and analysis.",
    ),
    IntentCategory(
        "L",
        "other",
        "No clear intent or an intent outside the listed classes.",
    ),
    IntentCategory("M", "other_obscene_or_illegal", "Obscene or illegal requests."),
)

CLASS_ORDER: tuple[str, ...] = tuple(category.code for category in INTENT_CATEGORIES)
INTENT_BY_CODE: dict[str, IntentCategory] = {
    category.code: category for category in INTENT_CATEGORIES
}


class ThradConversationClassifier:
    """Lazy ONNX runtime wrapper for Thrad's open-source conversation classifier."""

    def __init__(
        self,
        *,
        model_id: str = MODEL_ID,
        model_revision: str = MODEL_REVISION,
        tokenizer_id: str = TOKENIZER_ID,
        max_length: int = MAX_LENGTH,
        local_files_only: bool = False,
    ) -> None:
        self.model_id = model_id
        self.model_revision = model_revision
        self.tokenizer_id = tokenizer_id
        self.max_length = max_length
        self.local_files_only = local_files_only
        self._session = None
        self._tokenizer = None
        self._np = None

    def classify(self, conversation: str) -> IntentPrediction:
        self._ensure_loaded()
        inputs = self._tokenizer(
            conversation,
            return_tensors="np",
            truncation=True,
            max_length=self.max_length,
        )
        input_names = {item.name for item in self._session.get_inputs()}
        onnx_inputs = {
            name: value for name, value in inputs.items() if name in input_names
        }
        logits = self._session.run(None, onnx_inputs)[0][0]
        probabilities = _softmax(self._np, logits)
        index = int(self._np.argmax(probabilities))
        label = CLASS_ORDER[index]
        category = INTENT_BY_CODE[label]
        return IntentPrediction(
            label=label,
            label_name=category.name,
            confidence=float(probabilities[index]),
            model_id=self.model_id,
            model_revision=self.model_revision,
        )

    def _ensure_loaded(self) -> None:
        if self._session is not None and self._tokenizer is not None:
            return

        try:
            import numpy as np
            import onnxruntime as ort
            from huggingface_hub import hf_hub_download
            from transformers import AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Thrad classifier dependencies are not installed"
            ) from exc

        model_path = hf_hub_download(
            repo_id=self.model_id,
            filename="model.onnx",
            revision=self.model_revision,
            local_files_only=self.local_files_only,
        )
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.tokenizer_id,
            local_files_only=self.local_files_only,
        )
        self._session = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"],
        )
        self._np = np


def _softmax(np, logits):
    shifted = logits - np.max(logits)
    exp = np.exp(shifted)
    return exp / np.sum(exp)
