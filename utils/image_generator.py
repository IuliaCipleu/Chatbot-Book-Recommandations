"""
This module provides a utility to generate book cover images using OpenAI's DALL·E based
on book summaries.
"""
import openai

def generate_image_from_summary(title, summary, save_path="generated_image.png"):
    """
    Uses OpenAI's DALL·E to generate an image based on a book summary.
    Returns the image URL.
    """
    prompt = (
        f"Generate a suggestive, artistic book cover or scene for the book titled "
        f"'{title}', based on this summary:\n\n{summary}\n\n"
        "The image should capture the theme, atmosphere, and style of the story."
    )

    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None
