import anthropic
import base64
import httpx
from config import get_settings

settings = get_settings()


class ClaudeService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"

    async def analyze_photo(self, image_url: str, user_context: str | None = None) -> dict:
        """
        Analyze a photo using Claude's vision capabilities.
        Returns location identification and historical context.
        """
        # Download image and convert to base64
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(image_url)
            image_data = base64.standard_b64encode(response.content).decode("utf-8")

        # Determine media type from URL
        media_type = "image/jpeg"
        if image_url.lower().endswith(".png"):
            media_type = "image/png"
        elif image_url.lower().endswith(".webp"):
            media_type = "image/webp"
        elif image_url.lower().endswith(".gif"):
            media_type = "image/gif"

        # Build the prompt
        context_section = ""
        if user_context:
            context_section = f"""
The user has provided this additional context about the photo:
"{user_context}"

Use this context to help inform your analysis, but verify what you can see in the image.
"""

        prompt = f"""Analyze this travel photo and provide helpful information for someone trying to remember where it was taken and what they were looking at.
{context_section}
Please provide your analysis in the following format:

## Location
Identify the location shown in this photo. Include:
- Specific landmark, building, or place name (if identifiable)
- City and country
- Any notable geographic features
- If you cannot identify the exact location, describe what you can see and suggest possible locations

## Historical & Cultural Context
Provide interesting historical and cultural information about this location:
- Brief history of the landmark or area
- Cultural significance
- Interesting facts a visitor might want to know
- Any notable events that occurred here

If you cannot identify the location with certainty, be honest about that and provide your best assessment based on visual clues like architecture style, landscape, signage, or other contextual elements."""

        # Call Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )

        # Parse response
        full_response = message.content[0].text

        # Extract sections
        location_info = ""
        historical_context = ""

        if "## Location" in full_response:
            parts = full_response.split("## Historical")
            location_info = parts[0].replace("## Location", "").strip()
            if len(parts) > 1:
                historical_context = parts[1].replace("& Cultural Context", "").strip()

        return {
            "location_info": location_info or full_response,
            "historical_context": historical_context,
            "full_response": full_response,
        }


# Singleton instance
claude_service = ClaudeService()
