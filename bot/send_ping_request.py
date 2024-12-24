import requests
import logging
import os
import json
from logger_setup import setup_logger
from config import Config

# Setup logging
logger = setup_logger()

# Load configuration
config = Config()

def send_ping(ping_id):
    """
    Sends a POST request to the /send_ping endpoint with the given ping_id.

    Args:
        ping_id (int): The ID of the ping to be sent.

    Returns:
        None
    """
    try:
        # Get the base URL from the config
        base_url = config.FLASK_APP_BOT_BASE_URL

        # Construct the endpoint URL
        endpoint_url = f"{base_url}/send_ping"

        # Prepare the request payload
        header = {"X-Bot-Secret-Key": config.BOT_SECRET_KEY}
        payload = {"ping_id": ping_id}

        # Log the request
        logger.info(f"Sending POST request to {endpoint_url} with ping_id={ping_id}")

        # Make the POST request
        response = requests.post(endpoint_url, json=payload, headers=header)

        # Handle the response
        if response.ok:
            logger.info(f"Successfully sent ping {ping_id}. Response: {response.json()}")
        else:
            logger.error(
                f"Failed to send ping {ping_id}. Status code: {response.status_code}, "
                f"Response: {response.text}"
            )

    except requests.RequestException as e:
        logger.error(f"HTTP request failed for ping {ping_id}.")
        logger.exception(e)
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending ping {ping_id}.")
        logger.exception(e)


if __name__ == "__main__":
    import sys

    # Ensure a ping_id argument is provided
    if len(sys.argv) != 2:
        logger.error("Usage: python send_ping_request.py <ping_id>")
        sys.exit(1)

    try:
        # Get the ping_id from the command-line arguments
        ping_id = int(sys.argv[1])

        # Call the send_ping function
        send_ping(ping_id)

    except ValueError:
        logger.error("Invalid ping_id provided. Must be an integer.")
        sys.exit(1)
    except Exception as e:
        logger.error("An unexpected error occurred.")
        logger.exception(e)
        sys.exit(1)