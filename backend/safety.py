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

def is_dish_safe_from_title(title, tag_list):
    """
     Determines which dietary tags from the user's list are compatible with the dish
    based on common ingredients found online.

    Args:
        title (str): The title of the dish.
        tag_list (list of str): The list of dietary tags to evaluate for compatibility.

    Returns:
        list of str: A subset of tag_list containing compatible dietary tags.


    """

    # Full list of dietary categories for reference
    all_categories = ["vegan", "vegetarian", "kosher", "nut allergy", "halal", "dairy-free", "gluten-free"]

    # Prepare the messages for the chat completion
    messages = [
        {
            "role": "system",
            "content": (
                "You are a culinary expert that determines which dietary tags are compatible with a dish. "
                "Analyze the dish's typical ingredients and RETURN ONLY the compatible tags from the user's list "
                "as a comma-separated list. A tag is compatible if the dish normally meets that dietary requirement."
            )
        },
        {
            "role": "user",
            "content": (
               f"# Dish title: '{title}'\n"
                f"# D: {', '.join(tag_list)}\n\n"
                "# Steps"
                "Step 1. First, list the typical main ingredients for this dish. Name this list L.\n"
                "Step 2. Then, check each dietary tag in D's compatibility with the dish:\n"
                "- vegan: YES if L contains ONLY plant-based products (no meat, dairy, eggs, or fish)\n"
                "- vegetarian: YES L has no meat/fish\n"
                "- nut allergy: YES L has no nuts\n"
                "- gluten-free: YES if L has no wheat/barley/rye\n"
                "- halal: YES if the preparation of the ingredients in L for this dish typically follows halal requirements\n"
                "- dairy-free: YES if L has no milk products\n"
                "- kosher: YES if L and the dish typically follows kosher requirements\n\n"
                "Step 3. Verify that this list of compatible dietary tags is correct by re-referencing the main ingredients of this dish. Remember, we are only checking the dietary tags in D.\n"
                "Step 4. Ensure that the resulting list only has dietary tags that are also in D."
                "Step 5. Ensure that no tags in the resulting list repeat."
                "Step 6. IMPORTANT: Return ONLY the compatible tags as a simple comma-separated list.\n\n"
                "# For example:\n"
                "Input: 'Tofu Stir Fry' with tags [vegan, nut allergy, gluten-free]\n"
                "Step 1: Ingredients = tofu, vegetables, soy sauce, oil\n"
                "Step 2: vegan=yes (all plant-based), nut allergy=yes (no nuts), gluten-free=yes (if using tamari)\n"
                "Step 3: Output: vegan, nut allergy, gluten-free"
            )
        }
    ]

    try:
        # Call the OpenAI Chat Completion API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use 'gpt-4' if available
            messages=messages,
        )

        # Extract the assistant's reply
        ai_response = response.choices[0].message.content.strip()
        safe_categories = [cat.strip().lower() for cat in ai_response.split(',')]
        
        # Filter to ensure only valid categories from `all_categories` are returned
        valid_categories = [cat for cat in safe_categories if cat in all_categories]
        return valid_categories

    except Exception as e:
        # Enhanced error handling
        print("An error occurred while calling the OpenAI API.")
        print(f"Exception details: {e}")
        return []