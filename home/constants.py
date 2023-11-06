# Define constants for use throughout the application
from django.conf import settings

GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("non-binary", "Non-Binary"),
    ("empty", "Rather Not Say/Empty"),
]

AGE_CHOICES = [
    ("15-18", "15-18"),
    ("19-24", "19-24"),
    ("empty", "Empty"),
]

RELATIONSHIP_STATUS_CHOICES = [
    ("in_a_relationship", "In a Relationship"),
    ("single", "Single"),
    ("complicated", "It's Complicated"),
    ("empty", "Empty"),
]

# The model used to identify embeddings in content
# When changing this consider running update_content_embeddings management cmd
model = None
if settings.LOAD_TRANSFORMER_MODEL:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-mpnet-base-v2")
