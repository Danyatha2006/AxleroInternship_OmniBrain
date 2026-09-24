import clip
import torch
from PIL import Image

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"

model, preprocess = clip.load("ViT-B/32", device=device)

print("CLIP model loaded successfully!")

# Create/load a test image
image = Image.new("RGB", (224, 224), "white")

# Preprocess image
image_input = preprocess(image).unsqueeze(0).to(device)

# Generate image embedding
with torch.no_grad():
    image_embedding = model.encode_image(image_input)

# Convert to a normal Python list
image_vector = image_embedding[0].cpu().numpy().tolist()

print("Image embedding created successfully!")
print("Vector size:", len(image_vector))
print("First 5 values:", image_vector[:5])