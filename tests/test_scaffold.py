import memkit


def test_version():
    assert memkit.__version__ == "0.1.0"


def test_config_defaults():
    from memkit.config import CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL
    assert CHROMA_PATH == "chroma_data"
    assert COLLECTION_NAME == "memories"
    assert EMBED_MODEL == "all-MiniLM-L6-v2"
