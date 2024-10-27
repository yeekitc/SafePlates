import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_dish_safe(comment, tag_list):
    """
    Determines safe dietary categories for a dish based on user comment and unsafe tags.
    
    Args:
        comment (str): A comment about the dish.
        tag_list (list of str): List of tags indicating what allergies/restrictions the dish contains.
    
    Returns:
        list: List of dietary categories that are safe for this dish.
    """

    # Combine comments into a single string
    # combined_comments = "\n".join(comments)
    all_categories = ["vegan", "vegetarian", "kosher", "nut allergy", "halal", "dairy", "gluten"]

    # Prepare the messages for the chat completion
    messages = [
        {
            "role": "system",
            "content": (
                f"""You are an assistant that analyzes comments about a particular dish and dietary restrictions that we know this dish violates,
                then outputs a list of dietary restrictions that this dish is friendly to by following the steps listed below.
                
                P: {', '.join(all_categories)}

                Step 1: Extract the ingredients mentioned or implied in the given user comment. 
                Step 2: Based on the result of Step 1, determine which dietary restrictions in P this dish is not friendly to. Remember the definitions of each dietary restriction, including what people with them cannot eat. What can't vegans eat? 
                What can't vegetarians eat? What can't people who must eat kosher or halal food eat? What can't those with a nut allergy eat?
                What can't those who mustn't have dairy or gluten in their diets eat?
                Step 3: Concatenate the result of Step 2 to the provided list of known restrictions/allergens in the dish.
                Step 4: Compute the safe categories by finding the set difference of P and the result of Step 3.
                Step 5: Return the safe categories (the result of Step 4) as a Pythonic, comma-separated list of strings.
                """

            )
        },
        {
            "role": "user",
            "content": (
                f"Comment about the dish: {comment}\n"
                f"Known restrictions/allergens in the dish: {', '.join(tag_list)}\n\n"
                "Please respond ONLY with a comma-separated list of safe categories from the possible dietary restrictions list."
            )
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
        safe_categories = [cat.strip().lower() for cat in ai_response.split(',')]
        valid_categories = [cat for cat in safe_categories if cat in all_categories]
        return valid_categories

        # return ai_response 

    except Exception as e:
        # Enhanced error handling
        print("An error occurred while calling the OpenAI API.")
        print(f"Exception details: {e}")
        return []
    
# def is_dish_safe_from_title(title, tag_list):
#     """
#     Determines safe dietary categories for a dish based on its title.
    
#     Args:
#         title (str): The title of the dish.
#         tag_list (list of str): The list of dietary restrictions inputted
        
#     Returns:
#         String: A string that mentions all the dietary friendly of this dish.
#     """

#     # Combine comments into a single string
#     # combined_comments = "\n".join(comments)
#     all_categories = ["vegan", "vegetarian", "kosher", "nut allergy", "halal", "dairy", "gluten"]

#     # Prepare the messages for the chat completion
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 f"""You are an assistant that analyzes a particular dish based on its typical ingredients,
#                 then outputs a list of dietary restrictions that this dish is friendly to by following the steps listed below.
                
#                 P: {', '.join(all_categories)}

#                 Step 1: Determine the list of ingredients this dish likely contains by researching online about what's usually in this dish using the title provided by user of the dish. 
#                 Step 2: Determine which dietary restrictions of the tag_list the user provides that the ingredients to this dish violates from the list in you found in Part 1. Remember the definitions of each dietary restriction, 
#                 especially what people with them cannot eat. Vegans cannot eat meat (including seafood), dairy, eggs.
#                 Vegetarians cannot eat meat, including seafood. Food that hasn't been processed specially does not qualify for kosher or halal. Those with a nut allergy cannot eat any type of nuts.
#                 What ingredients can't those who mustn't have dairy or gluten in their diets eat?
#                 Step 3: After filtering out tag_list by Step 2 (which filters out the dietary restriction types that are found within the ingredients of this dish), respond with 'approved for No list of resulting item from Step 2 separated by commas
#                 """

#             )
#         },
#         {
#             "role": "user",
#             "content": (
#                 f"Dish: {title}\n"
#                 f"Restrictions/allergens that are looked out for in the dish: {', '.join(tag_list)}\n\n"
#                 "Please respond ONLY with a string of the comma-separated list of safe categories from the possible dietary restrictions list tag_list."
#             )
#         }
#     ]

#     try:
#         # Call the OpenAI Chat Completion API
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",  # Use 'gpt-4' if you have access
#             messages=messages,
#             max_tokens=150,
#             temperature=0,
#             n=1,
#         )

#         # Extract the assistant's reply
#         ai_response = response.choices[0].message.content.strip()
#         safe_categories = [cat.strip().lower() for cat in ai_response.split(',')]
#         valid_categories = [cat for cat in safe_categories if cat in all_categories]
#         return valid_categories

#         # return ai_response 

#     except Exception as e:
#         # Enhanced error handling
#         print("An error occurred while calling the OpenAI API.")
#         print(f"Exception details: {e}")
#         return []

# def is_dish_safe_from_title(title, tag_list):
#     """
#      Determines which dietary tags from the user's list are compatible with the dish
#     based on common ingredients found online.

#     Args:
#         title (str): The title of the dish.
#         tag_list (list of str): The list of dietary tags to evaluate for compatibility.

#     Returns:
#         list of str: A subset of tag_list containing compatible dietary tags.


#     """

#     # Full list of dietary categories for reference
#     all_categories = ["vegan", "vegetarian", "kosher", "nut allergy", "halal", "dairy-free", "gluten-free"]

#     # Prepare the messages for the chat completion
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are a dietary assistant that evaluates whether a dish is compatible with specific dietary tags. "
#             "Using the dish title and a list of known dietary restrictions, your task is to determine which tags are safe for the dish."
            
#             "Steps to follow:"
#             "\n1. Identify the main ingredients implied by the dish title, focusing only on common components (e.g., 'hot dog' contains meat)."
#             "\n2. Compare each dietary tag (that also appears in the original tag_list provided as input) against the implied ingredients. For each tag (that also appears in the original tag_list provided as input), follow these rules:"
#             "\n   - Vegan: The dish is not vegan if it contains meat, dairy, eggs, or fish."
#             "\n   - Vegetarian: The dish is not vegetarian if it contains meat or fish."
#             "\n   - Nut allergy: The dish is not nut-allergy safe if it contains nuts."
#             "\n   - Dairy-free: The dish is not dairy-free if it contains milk or dairy products."
#             "\n   - Gluten-free: The dish is not gluten-free if it contains wheat, barley, or rye."
#             "\n   - Kosher: Assume the dish is not kosher unless specified."
#             "\n   - Halal: Assume the dish is not halal unless specified."
            
#             "\n3. Remove any incompatible tags based on the known dietary restrictions (e.g., if the dish is 'hot dog,' automatically exclude vegan and vegetarian)."
#             "\n4. Respond ONLY with a comma-separated list of compatible tags."
#             )
#         },
#         {
#             "role": "user",
#             "content": (
#                 f"Dish title: '{title}'\n"
#                 f"Known restrictions/allergens in the dish: {', '.join(tag_list)}\n\n"
#                 "Please respond ONLY with a comma-separated list of compatible dietary tags."
#             )
#         }
#     ]

#     try:
#         # Call the OpenAI Chat Completion API
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",  # Use 'gpt-4' if available
#             messages=messages,
#         )

#         # Extract the assistant's reply
#         ai_response = response.choices[0].message.content.strip()
#         safe_categories = [cat.strip().lower() for cat in ai_response.split(',')]
        
#         # Filter to ensure only valid categories from `all_categories` are returned
#         valid_categories = [cat for cat in safe_categories if cat in all_categories]
#         return valid_categories

#     except Exception as e:
#         # Enhanced error handling
#         print("An error occurred while calling the OpenAI API.")
#         print(f"Exception details: {e}")
#         return []