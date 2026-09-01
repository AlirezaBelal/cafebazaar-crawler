import random
import string
import os
from pathlib import Path


def generate_random_string(length=32):
    # Create a pool of characters: lowercase letters and digits
    characters = string.ascii_lowercase + string.digits

    # Randomly choose characters from the pool to create a string of the desired length
    random_string = ''.join(random.choice(characters) for _ in range(length))

    return random_string


# Generate random device ID for each session
DEVICE_ID = generate_random_string()

# Delay settings (in milliseconds)
SLEEP_AFTER_EACH_CATEGORIES_IN_MILL_SECONDS = 10000
SLEEP_AFTER_EACH_SUB_CATEGORIES_IN_MILL_SECONDS = 2000
SLEEP_AFTER_EACH_APPS_IN_MILL_SECONDS = 100

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

os.makedirs(DATA_DIR, exist_ok=True)

# Set the path for the database file
RESULT_FILE = os.path.join(DATA_DIR, 'cafebazaar_results.db')