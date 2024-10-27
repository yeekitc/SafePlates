import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Create an OpenAI client instance
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_dish_vegan(comments):
    """
    Determines if a dish is vegan-friendly based on user comments.

    Args:
        comments (list of str): A list of comments about the dish.

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
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Hardcoded mock comments about the dish
    comments = [
        "This salad was amazing and so fresh!",
        "I loved the dressing, but I'm pretty sure it had honey in it.",
        "The inclusion of goat cheese really added a nice flavor.",
        "I'm vegan and appreciated the variety of vegetables.",
        "Beware, the croutons are made with butter.",
    ]

    result = is_dish_vegan(comments)
    if result:
        print("Result:")
        print(result)
    else:
        print("Failed to determine if the dish is vegan-friendly.")