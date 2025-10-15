from pathlib import Path
import bioacoustics_model_zoo as bmz
import opensoundscape
import torch


def load_bmz_model(model_name, logger=None):
    """Load a model from the bioacoustics model zoo"""
    try:
        if logger:
            logger.info(f"Loading model: {model_name}")

        # Load model using the same approach as streamlit_inference.py
        model = getattr(bmz, model_name)()
        if logger:
            logger.info(f"Model loaded successfully: {type(model).__name__}")
        return model
    except ImportError as e:
        if logger:
            logger.error(
                f"Import error - make sure bioacoustics_model_zoo is installed: {e}"
            )
        raise
    except AttributeError as e:
        if logger:
            logger.error(f"Model {model_name} not found in bioacoustics_model_zoo: {e}")
        raise
    except Exception as e:
        if logger:
            logger.error(f"Failed to load model {model_name}: {e}")
        raise


def load_model(config_data, logger=None):
    model_source = config_data.get("model_source")
    if model_source == "bmz":
        model_name = config_data.get("model")
        if not model_name:
            raise ValueError("Model name for BMZ model not specified in config")
        model = load_bmz_model(model_name, logger=logger)
    elif model_source == "local_file":  # local file model
        model_name = "local model"
        # Special case for local file model
        model_path = config_data.get("model", None)
        if not Path(model_path).is_file():
            raise ValueError(
                f"Local OpenSoundscape CNN model file '{model_path}' not found"
            )
        model = torch.load(model_path, weights_only=False, map_location="cpu")
        model.device = opensoundscape.ml.cnn._gpu_if_available()
        model.network.to(model.device)
        # TODO: avoid save/load of pickles, use dictionaries and state dicts
        # but this gets complicated when supporting various model types
    elif model_source == "mlp_classifier":
        from opensoundscape.ml.shallow_classifier import MLPClassifier

        model = MLPClassifier.load(config_data.get("model"))
    else:
        raise ValueError(f"Unknown model source: {model_source}")

    return model
