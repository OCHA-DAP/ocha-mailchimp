import os
from loguru import logger
import requests
import hashlib

# Mailchimp API configuration
api_key = os.getenv('MAILCHIMP_API_KEY')
server_prefix = os.getenv('SERVER_PREFIX')  # Replace with your server prefix (e.g., us1, us2)

# Base URL for the API
BASE_URL = f"https://{server_prefix}.api.mailchimp.com/3.0"

# Headers with authentication
HEADERS = {
    "Authorization": f"Bearer {api_key}"
}


def get_subscribers(list_id: str) -> list:
    """
    Fetches all subscribers for a specified 'list_id'.

    Args:
        list_id: list identifier

    Returns:

    """
    url = f"{BASE_URL}/lists/{list_id}/members"
    params = {
        "status": "subscribed",  # Fetch only active subscribers
        "count": 1000,  # Maximum number of results per request
    }
    headers = HEADERS

    all_subscribers = []
    offset = 0

    while True:
        # Update offset for pagination
        params["offset"] = offset
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            all_subscribers.extend(data["members"])

            # Break if there are no more records
            if len(data["members"]) < params["count"]:
                break
            offset += params["count"]
        else:
            logger.error(f"Failed to retrieve subscribers: {response.json()}")
            break

    return all_subscribers


def add_subscriber_to_group(email:str, new_group_id: str, list_id: str):
    """
    Adds a subscriber of a specified 'list_id' to a group identified by 'new_group_id'.
    Args:
        email: email address of the subscriber to be added
        new_group_id: group identifier
        list_id: list identifier
    """
    hashed_email = get_subscriber_hash(email=email)
    url = f"https://{server_prefix}.api.mailchimp.com/3.0/lists/{list_id}/members/{hashed_email}"

    payload = {
        "interests": {new_group_id: True}  # True to add the subscriber to the group
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.patch(url, json=payload, headers=headers)
    if response.status_code == 200:
        logger.info(f"Subscriber {email} updated successfully.")
    else:
        logger.error(f"Failed to update {email}: {response.json()}")



def get_interest_categories(list_id: str) -> list:
    """
    Fetches all interest categories for a specified 'list_id'.
    Args:
        list_id: list identifier

    Returns: list of interest categories
    """
    url = f"{BASE_URL}/lists/{list_id}/interest-categories"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["categories"]
    else:
        logger.error(f"Error: {response.status_code} - {response.json()}")
        return []

def get_interests(list_id: str, category_id: str) -> list:
    """
    Fetches all interests given an interest category for a specified 'list_id'.
    Args:
        list_id: list identifier
        category_id: category identifier

    Returns: list of interests
    """
    url = f"{BASE_URL}/lists/{list_id}/interest-categories/{category_id}/interests"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["interests"]
    else:
        logger.error(f"Error: {response.status_code} - {response.json()}")
        return []


def get_subscriber_hash(email):
    hashed_email = hashlib.md5(email.lower().encode()).hexdigest()
    return hashed_email


# Function to retrieve subscribers with a specific interest
def get_subscribers_with_interest(list_id, interest_id):
    url = f"{BASE_URL}/lists/{list_id}/members"
    params = {
        "fields": "members.email_address",  # Retrieve only the email addresses
        "interest_id": interest_id,  # Filter by interest ID
        "status": "subscribed",  # Only fetch active subscribers
        "count": 1000  # Adjust as needed
    }


    response = requests.get(url, headers=HEADERS  , params=params)
    if response.status_code == 200:
        return [member["email_address"] for member in response.json()["members"]]
    else:
        print(f"Failed to fetch subscribers. Error: {response.status_code} - {response.json()}")
        return []

# Function to add a tag to a subscriber
def add_tag_to_subscriber(email, tag_name, list_id):
    subscriber_hash = get_subscriber_hash(email)
    url = f"{BASE_URL}/lists/{list_id}/members/{subscriber_hash}/tags"

    payload = {
        "tags": [
            {"name": tag_name, "status": "active"}  # Use "inactive" to remove the tag
        ]
    }


    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 204:
        print(f"Tag '{tag_name}' successfully added to {email}.")
    else:
        print(f"Failed to add tag to {email}. Error: {response.status_code} - {response.json()}")

# Main logic
def add_tag_to_interest_subscribers(list_id, interest_id, tag_name):
    # Step 1: Fetch all subscribers with the specific interest
    subscribers = get_subscribers_with_interest(list_id=list_id, interest_id=interest_id, tag_name=tag_name)
    if not subscribers:
        print("No subscribers found for the specified interest.")
        return

    # Step 2: Add the tag to each subscriber
    for email in subscribers:
        add_tag_to_subscriber(email, tag_name=tag_name)