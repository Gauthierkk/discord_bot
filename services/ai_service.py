"""
AI service for Ollama integration and prompt generation
"""

import json
from typing import Dict, List

import aiohttp
import ollama

from config import logger


def build_summary_prompt(
    messages_text: str, time_desc: str, has_images: bool = False
) -> str:
    """
    Build a prompt for AI summarization

    Args:
        messages_text: Formatted messages string
        time_desc: Description of time period (e.g., "past 3 days")
        has_images: Whether the conversation includes images

    Returns:
        Formatted prompt string
    """
    if has_images:
        image_instruction = """
IMPORTANT: The conversation includes images that have been analyzed by a vision AI.
The IMAGE CONTEXT section contains descriptions of these images.
When generating the summary, integrate the image information naturally throughout:
- Include image-related topics in "main_topics"
- Mention visual content in "key_points" where relevant
- Reference images in "notable_moments" if they're significant
- Let the images inform your understanding of the conversation's "overview"
"""
    else:
        image_instruction = ""

    return f"""Analyze the following Discord channel conversation from the {time_desc} and provide a structured summary.
{image_instruction}
Please respond ONLY with valid JSON in the following format:
{{
  "overview": "A 2-3 sentence overview of the conversation (incorporate image context if present)",
  "main_topics": ["topic1", "topic2", "topic3"],
  "key_points": ["point1", "point2", "point3"],
  "sentiment": "positive/neutral/negative",
  "notable_moments": "Any interesting or important moments (optional)"
}}

Messages:
{messages_text}

Remember to respond ONLY with valid JSON, no other text."""


async def download_image(url: str) -> bytes:
    """
    Download an image from a URL

    Args:
        url: Image URL

    Returns:
        Image bytes
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"Failed to download image: {response.status}")


async def analyze_images(image_urls: List[str], vision_model: str = "llava") -> str:
    """
    Analyze images using a vision model

    Args:
        image_urls: List of image URLs
        vision_model: Vision-capable Ollama model

    Returns:
        Description of the images
    """
    if not image_urls:
        return ""

    logger.info(f"Analyzing {len(image_urls)} image(s) with {vision_model}")

    # Limit to first 5 images to avoid overload
    limited_urls = image_urls[:5]

    descriptions = []
    for idx, url in enumerate(limited_urls, 1):
        try:
            # Download image
            image_data = await download_image(url)

            # Analyze with vision model
            response = ollama.generate(
                model=vision_model,
                prompt="Describe this image briefly in one sentence.",
                images=[image_data],
            )

            descriptions.append(f"Image {idx}: {response['response'].strip()}")
        except Exception as e:
            logger.error(f"Error analyzing image {idx}: {e}")
            descriptions.append(f"Image {idx}: [Could not analyze]")

    return "\n".join(descriptions)


async def generate_summary(
    messages_text: str,
    time_desc: str,
    image_urls: List[str] = None,
    model: str = "gpt-oss:20b-cloud",
    vision_model: str = "llava",
) -> Dict:
    """
    Generate AI summary using Ollama

    Args:
        messages_text: Formatted messages string
        time_desc: Description of time period
        image_urls: List of image URLs to analyze
        model: Ollama model to use for text
        vision_model: Ollama model to use for images

    Returns:
        Parsed JSON summary data

    Raises:
        Exception: If Ollama request fails
        json.JSONDecodeError: If response is not valid JSON
    """
    # Analyze images if present and add as context
    has_images = False

    if image_urls and len(image_urls) > 0:
        try:
            logger.info(
                f"Analyzing {len(image_urls)} images to provide context for summary..."
            )
            images_description = await analyze_images(image_urls, vision_model)

            if images_description:
                # Explicitly add image context to the conversation
                messages_text += f"\n\n{'=' * 50}\nIMAGE CONTEXT (analyzed by vision AI):\n{'=' * 50}\n{images_description}\n{'=' * 50}"
                has_images = True
                logger.info(
                    "Successfully analyzed images, added context to summary prompt"
                )
            else:
                logger.warning("Image analysis returned no descriptions")
        except Exception as e:
            logger.error(f"Error analyzing images: {e}")
            logger.warning("Continuing with text-only summary")

    # Build prompt with or without image context
    prompt = build_summary_prompt(messages_text, time_desc, has_images)

    logger.info(
        f"Generating summary with Ollama model: {model} (with{'out' if not has_images else ''} image context)"
    )

    # Call Ollama
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

    summary_text = response["message"]["content"].strip()

    # Clean up markdown code blocks if present
    summary_text = clean_json_response(summary_text)

    # Parse JSON
    summary_data = json.loads(summary_text)

    return summary_data


def clean_json_response(text: str) -> str:
    """
    Remove markdown code blocks from JSON response

    Args:
        text: Raw response text

    Returns:
        Cleaned text ready for JSON parsing
    """
    # Sometimes the model adds markdown code blocks, remove them
    if text.startswith("```json"):
        text = text.split("```json")[1]
    if text.startswith("```"):
        text = text.split("```")[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    return text.strip()
