import os
from huggingface_hub import InferenceClient

# Set the new token provided by the user
# os.environ["HF_TOKEN"] = "hf_..." # Removed for security
if not os.environ.get("HF_TOKEN"):
    print("HF_TOKEN not set, skipping test")
    exit(0)

print("Starting Hugging Face Image Gen Test (Key 2)...")

try:
    client = InferenceClient(
        provider="together",
        api_key=os.environ["HF_TOKEN"],
    )

    print("Sending request to black-forest-labs/FLUX.1-dev...")
    
    # output is a PIL.Image object
    image = client.text_to_image(
        "A dragon flying over a medieval castle",
        model="black-forest-labs/FLUX.1-dev",
    )
    
    output_path = "test_hf_result.png"
    image.save(output_path)
    print(f"Success! Image saved to {output_path}")

except Exception as e:
    print(f"Error: {e}")
