import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_dish_safe(comments, criteria):
    """
    Determines if a dish is safe for a specific dietary restriction based on user comments.
    Primarily used for detecting allergens.

    Args:
        comments (list of str): A list of comments about the dish.
        criteria (str): The dietary criteria to check for (e.g., "nut", "gluten").

    Returns:
        str: Message indicating if the dish is safe for the specified criteria or not.
    """

    # Combine comments into a single string
    combined_comments = "\n".join(comments)

    # Prepare the messages for the chat completion
    messages = [
        {
            "role": "system",
            "content": f"You are an assistant that checks if a dish is safe for someone with '{criteria}' allergies based on user comments. If the dish contains '{criteria}', respond with 'Not {criteria.capitalize()}-friendly' and provide a brief explanation. Otherwise, respond with '{criteria.capitalize()}-friendly'."
        },
        {
            "role": "user",
            "content": f"Comments about the dish:\n{combined_comments}\n\nPlease respond with either '{criteria.capitalize()}-friendly' or 'Not {criteria.capitalize()}-friendly' and provide a brief explanation."
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
        return f"Error: Unable to determine if the dish is {criteria}-friendly."


