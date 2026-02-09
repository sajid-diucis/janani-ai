import os
from huggingface_hub import InferenceClient

# Using the same token
# os.environ["HF_TOKEN"] = "hf_..." # Removed for security
if not os.environ.get("HF_TOKEN"):
    print("HF_TOKEN not set, skipping test")
    exit(0)

print("Testing Standard Serverless API (No Provider)...")

try:
    # REMOVED provider="together" to try the standard free tier
    client = InferenceClient(api_key=os.environ["HF_TOKEN"])

    print("Requesting image from runwayml/stable-diffusion-v1-5...")
    
    image = client.text_to_image(
        "A simple red apple",
        model="runwayml/stable-diffusion-v1-5",
    )
    
    image.save("test_free_tier.png")
    print("Success! Generated on free tier.")

except Exception as e:
    print(f"Error: {e}")
