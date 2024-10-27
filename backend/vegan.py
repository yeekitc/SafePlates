import openai
import os
from dotenv import load_dotenv

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
load_dotenv()

def is_dish_vegan(comments):
    """
    Determines if a dish is vegan-friendly based on user comments.

    Args:
        comments (list of str): A list of comments about the dish.
        api_key (str): OpenAI API key.

    Returns:
        str: 'Vegan-friendly' or 'Not vegan-friendly' based on analysis.
    """

    # Combine comments into a single string
    combined_comments = "\n".join(comments)

    # Prepare the messages for the chat completion
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that determines if a dish is vegan-friendly based on user comments."
        },
        {
            "role": "user",
            "content": f"Comments about the dish:\n{combined_comments}\n\nPlease respond with either 'Vegan-friendly' or 'Not vegan-friendly' and provide a brief explanation."
        }
    ]

    try:
        # Call the OpenAI Chat Completion API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use 'gpt-4' if you have access
            messages=messages,
            max_tokens=150,
            temperature=0,
            n=1,
        )

        # Extract the assistant's reply
        ai_response = response.choices[0].message.content.strip()
        return ai_response

    except Exception as e:
        # Enhanced error handling
        print("An error occurred while calling the OpenAI API.")
        print(f"Exception details: {e}")
        return "Error: Unable to determine if the dish is vegan-friendly."


