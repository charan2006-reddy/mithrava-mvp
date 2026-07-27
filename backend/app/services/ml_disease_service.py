"""ML-based disease detection using pre-trained MobileNetV2.

Uses a HuggingFace pre-trained model for fast, free disease detection.
Falls back to GPT-4o Vision when confidence is low.
"""

import io
import logging
from typing import Optional

import torch
import torchvision.transforms as transforms
from PIL import Image
from huggingface_hub import hf_hub_download

logger = logging.getLogger("mithrava.ml_disease")

# 38 classes from PlantVillage dataset
CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

# Human-readable disease names
DISEASE_LABELS = {
    "Apple___Apple_scab": "Apple Scab",
    "Apple___Black_rot": "Apple Black Rot",
    "Apple___Cedar_apple_rust": "Cedar Apple Rust",
    "Apple___healthy": "Healthy Apple",
    "Blueberry___healthy": "Healthy Blueberry",
    "Cherry_(including_sour)___Powdery_mildew": "Cherry Powdery Mildew",
    "Cherry_(including_sour)___healthy": "Healthy Cherry",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn Gray Leaf Spot",
    "Corn_(maize)___Common_rust_": "Corn Common Rust",
    "Corn_(maize)___Northern_Leaf_Blight": "Corn Northern Leaf Blight",
    "Corn_(maize)___healthy": "Healthy Corn",
    "Grape___Black_rot": "Grape Black Rot",
    "Grape___Esca_(Black_Measles)": "Grape Esca (Black Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Grape Leaf Blight",
    "Grape___healthy": "Healthy Grape",
    "Orange___Haunglongbing_(Citrus_greening)": "Citrus Greening (Huanglongbing)",
    "Peach___Bacterial_spot": "Peach Bacterial Spot",
    "Peach___healthy": "Healthy Peach",
    "Pepper,_bell___Bacterial_spot": "Pepper Bacterial Spot",
    "Pepper,_bell___healthy": "Healthy Pepper",
    "Potato___Early_blight": "Potato Early Blight",
    "Potato___Late_blight": "Potato Late Blight",
    "Potato___healthy": "Healthy Potato",
    "Raspberry___healthy": "Healthy Raspberry",
    "Soybean___healthy": "Healthy Soybean",
    "Squash___Powdery_mildew": "Squash Powdery Mildew",
    "Strawberry___Leaf_scorch": "Strawberry Leaf Scorch",
    "Strawberry___healthy": "Healthy Strawberry",
    "Tomato___Bacterial_spot": "Tomato Bacterial Spot",
    "Tomato___Early_blight": "Tomato Early Blight",
    "Tomato___Late_blight": "Tomato Late Blight",
    "Tomato___Leaf_Mold": "Tomato Leaf Mold",
    "Tomato___Septoria_leaf_spot": "Tomato Septoria Leaf Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Tomato Spider Mites",
    "Tomato___Target_Spot": "Tomato Target Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato Yellow Leaf Curl Virus",
    "Tomato___Tomato_mosaic_virus": "Tomato Mosaic Virus",
    "Tomato___healthy": "Healthy Tomato",
}

# Mapping from raw class name to crop name
CROP_MAPPING = {
    "Apple": "Apple",
    "Blueberry": "Blueberry",
    "Cherry": "Cherry",
    "Corn": "Corn/Maize",
    "Grape": "Grape",
    "Orange": "Orange/Citrus",
    "Peach": "Peach",
    "Pepper": "Pepper",
    "Potato": "Potato",
    "Raspberry": "Raspberry",
    "Soybean": "Soybean",
    "Squash": "Squash",
    "Strawberry": "Strawberry",
    "Tomato": "Tomato",
}

# Treatment database for detected diseases
TREATMENT_DB = {
    "Tomato___Early_blight": {
        "organic": [
            "Spray neem oil (5ml/L water) every 7 days",
            "Apply Trichoderma viride (2g/L) as soil drench",
            "Remove and destroy affected leaves immediately",
            "Mulch around plants to prevent soil splash",
        ],
        "chemical": [
            "Mancozeb 75% WP @ 2g/L as foliar spray",
            "Chlorothalonil 75% WP @ 2g/L - repeat after 10 days",
            "Hexaconazole 5% EC @ 2ml/L for severe cases",
        ],
        "prevention": [
            "Use resistant tomato varieties",
            "Maintain proper plant spacing (60cm)",
            "Avoid overhead irrigation",
            "Practice crop rotation for 2 years",
        ],
    },
    "Tomato___Late_blight": {
        "organic": [
            "Apply copper-based organic fungicide",
            "Remove affected plants immediately",
            "Improve air circulation between plants",
        ],
        "chemical": [
            "Metalaxyl + Mancozeb @ 2.5g/L",
            "Fosetyl Aluminium @ 2g/L",
            "Copper oxychloride @ 3g/L",
        ],
        "prevention": [
            "Use resistant varieties",
            "Avoid overhead watering",
            "Ensure good drainage",
        ],
    },
    "Potato___Early_blight": {
        "organic": [
            "Remove infected leaves",
            "Apply neem oil spray",
            "Use mulch to prevent soil splash",
        ],
        "chemical": [
            "Mancozeb 75% WP @ 2g/L",
            "Difenoconazole 25% EC @ 1ml/L",
        ],
        "prevention": [
            "Rotate crops every 2-3 years",
            "Use certified seed potatoes",
            "Maintain balanced fertilization",
        ],
    },
    "Potato___Late_blight": {
        "organic": [
            "Remove and destroy infected plants",
            "Apply copper spray",
            "Improve drainage",
        ],
        "chemical": [
            "Metalaxyl + Mancozeb @ 2.5g/L",
            "Dimethomorph + Mancozeb @ 2g/L",
        ],
        "prevention": [
            "Use resistant varieties",
            "Avoid overhead irrigation",
            "Monitor weather conditions",
        ],
    },
    "Corn_(maize)___Common_rust_": {
        "organic": [
            "Remove heavily infected leaves",
            "Use resistant hybrids next season",
        ],
        "chemical": [
            "Propiconazole 25 EC @ 1ml/L",
            "Tebuconazole 25.9 EC @ 1ml/L",
        ],
        "prevention": [
            "Plant resistant hybrids",
            "Early planting reduces severity",
        ],
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "organic": [
            "Rotate crops",
            "Remove crop debris",
        ],
        "chemical": [
            "Azoxystrobin 23 SC @ 1ml/L",
            "Propiconazole 25 EC @ 1ml/L",
        ],
        "prevention": [
            "Use resistant hybrids",
            "Practice crop rotation",
        ],
    },
}


class MLDiseaseService:
    """Service for ML-based disease detection using pre-trained MobileNetV2."""

    _model = None
    _transform = None
    _initialized = False

    @classmethod
    def initialize(cls) -> bool:
        """Load the pre-trained MobileNetV2 model from HuggingFace.

        Downloads the model weights on first call and caches them.
        Returns True if initialization was successful.
        """
        if cls._initialized:
            return True

        try:
            from torchvision import models

            logger.info("Loading MobileNetV2 model from HuggingFace...")

            # Download model weights from HuggingFace
            model_path = hf_hub_download(
                repo_id="Daksh159/plant-disease-mobilenetv2",
                filename="mobilenetv2_plant.pth",
            )

            # Create MobileNetV2 architecture
            model = models.mobilenet_v2(pretrained=False)
            model.classifier[1] = torch.nn.Sequential(
                torch.nn.Dropout(0.2),
                torch.nn.Linear(model.classifier[1].in_features, 38),
            )

            # Load pre-trained weights
            state_dict = torch.load(model_path, map_location="cpu", weights_only=True)
            model.load_state_dict(state_dict)
            model.eval()

            # Define image preprocessing
            transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ])

            cls._model = model
            cls._transform = transform
            cls._initialized = True

            logger.info("MobileNetV2 model loaded successfully!")
            return True

        except Exception as exc:
            logger.error("Failed to load MobileNetV2 model: %s", exc)
            return False

    @classmethod
    async def predict(cls, image_bytes: bytes) -> dict:
        """Predict disease from an image using the pre-trained model.

        Args:
            image_bytes: Raw image bytes.

        Returns:
            Dict with prediction results including disease name,
            confidence, crop type, and treatment recommendations.
        """
        if not cls._initialized:
            if not cls.initialize():
                return {
                    "success": False,
                    "error": "ML model not available",
                    "fallback_to_gpt4": True,
                }

        try:
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            input_tensor = cls._transform(image).unsqueeze(0)

            # Run inference
            with torch.no_grad():
                outputs = cls._model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

            # Get top prediction
            confidence, predicted_idx = torch.max(probabilities, 0)
            confidence_pct = confidence.item() * 100
            predicted_class = CLASS_NAMES[predicted_idx.item()]

            # Get top 3 predictions
            top3_probs, top3_indices = torch.topk(probabilities, 3)
            top3 = []
            for i in range(3):
                idx = top3_indices[i].item()
                prob = top3_probs[i].item() * 100
                top3.append({
                    "disease": DISEASE_LABELS.get(CLASS_NAMES[idx], CLASS_NAMES[idx]),
                    "confidence": round(prob, 1),
                    "is_healthy": "healthy" in CLASS_NAMES[idx].lower(),
                })

            # Parse crop and disease from class name
            parts = predicted_class.split("___")
            crop_raw = parts[0]
            disease_raw = parts[1] if len(parts) > 1 else "healthy"

            crop_name = CROP_MAPPING.get(crop_raw, crop_raw)
            is_healthy = "healthy" in disease_raw.lower()
            disease_name = "Healthy" if is_healthy else DISEASE_LABELS.get(predicted_class, disease_raw.replace("_", " "))

            # Get treatment from database
            treatment = TREATMENT_DB.get(predicted_class, {})

            return {
                "success": True,
                "method": "MobileNetV2",
                "crop_detected": crop_name,
                "disease_name": disease_name,
                "confidence": round(confidence_pct, 1),
                "is_healthy": is_healthy,
                "severity": _confidence_to_severity(confidence_pct, is_healthy),
                "top_predictions": top3,
                "treatment": treatment if not is_healthy else {},
                "needs_gpt4_fallback": confidence_pct < 70,
            }

        except Exception as exc:
            logger.error("ML prediction failed: %s", exc)
            return {
                "success": False,
                "error": str(exc),
                "fallback_to_gpt4": True,
            }


def _confidence_to_severity(confidence: float, is_healthy: bool) -> str:
    """Convert confidence score to severity level."""
    if is_healthy:
        return "low"
    if confidence >= 90:
        return "high"
    if confidence >= 75:
        return "medium"
    return "low"
