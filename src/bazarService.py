import json
import random
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config
from models.AppDetails import AppDetails, Source


# Configure retry strategy
def get_session():
    session = requests.Session()
    retry = Retry(
        total=5,  # Maximum number of retries
        backoff_factor=0.5,  # Backoff factor for sleep time between retries
        status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry on
        allowed_methods=["POST", "GET"],  # HTTP methods to retry on
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def get_cafebazaar_categories():
    """
    Fetches all categories from the CafeBazaar Android app store.

    Returns:
        list: A list of dictionaries, each representing a category with details like icon URL, title, info, and path.
    """
    url = "https://api.cafebazaar.ir/rest-v1/process/GetPageV2Request"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://cafebazaar.ir",
        "Priority": "u=1, i",
        "Referer": "https://cafebazaar.ir/",
        "Sec-CH-UA": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/129.0.0.0 Safari/537.36"
    }

    payload = {
        "properties": {
            "language": 2,
            "clientID": config.DEVICE_ID,
            "deviceID": config.DEVICE_ID,
            "clientVersion": "web"
        },
        "singleRequest": {
            "getPageV2Request": {
                "path": "all-categories-and-genres"
            }
        }
    }

    try:
        session = get_session()
        response = session.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()

        # Navigate through the JSON structure to extract categories
        categories = []
        tabs = data.get("singleReply", {}) \
            .get("getPageV2Reply", {}) \
            .get("page", {}) \
            .get("tabs", {}) \
            .get("tabs", [])

        for tab in tabs:
            rows = tab.get("pageBodyInfo", {}) \
                .get("pageBody", {}) \
                .get("rows", [])

            for row in rows:
                category_info = row.get("categoryItem", {}).get("info", {})
                category = {
                    "icon": category_info.get("icon"),
                    "title": category_info.get("title"),
                    "info": category_info.get("info"),
                    "path": category_info.get("path")
                }
                categories.append(category)

        return categories

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Handle HTTP errors
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")  # Handle other request errors
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")  # Handle JSON decoding errors
    except Exception as err:
        print(f"An unexpected error occurred: {err}")  # Handle any other exceptions

    return []  # Return an empty list in case of errors


def fetch_all_subcategories(category_path):
    api_url = "https://api.cafebazaar.ir/rest-v1/process/GetPageBodyRequest"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://cafebazaar.ir",
        "priority": "u=1, i",
        "referer": "https://cafebazaar.ir/",
        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    all_subcategories = []
    offset = 0
    consecutive_errors = 0
    max_errors = 3

    while True:
        payload = {
            "properties": {
                "language": 2,
                "clientID": config.DEVICE_ID,
                "deviceID": config.DEVICE_ID,
                "clientVersion": "web"
            },
            "singleRequest": {
                "getPageBodyRequest": {
                    "path": category_path,
                    "offset": offset
                }
            }
        }

        try:
            session = get_session()
            response = session.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            consecutive_errors = 0

            subcategories = extract_subcategories(response.json())
            if not subcategories:
                break

            all_subcategories.extend(subcategories)
            offset += len(subcategories)
            time.sleep(random.uniform(0.5, 1.5))
        except Exception as exc:
            consecutive_errors += 1
            print(f"Error fetching subcategories ({consecutive_errors}/{max_errors}): {exc}")
            if consecutive_errors >= max_errors:
                break
            time.sleep(random.uniform(2, 5))

    return all_subcategories


def extract_subcategories(response_data):
    # Extract simpleAppList title and vitrinExpandInfo path
    subcategories = []
    rows = response_data.get('singleReply', {}).get('getPageBodyReply', {}).get('pageBody', {}).get('rows', [])

    for row in rows:
        if 'simpleAppList' in row:
            title = row['simpleAppList'].get('title')
            path = row['simpleAppList'].get('expandInfo', {}).get('vitrinExpandInfo', {}).get('path')
            if title and path:
                subcategories.append({
                    "title": title,
                    "path": path
                })

    return subcategories


def fetch_all_apps(subcategory_path):
    api_url_v2 = "https://api.cafebazaar.ir/rest-v1/process/GetPageV2Request"
    api_url_body = "https://api.cafebazaar.ir/rest-v1/process/GetPageBodyRequest"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://cafebazaar.ir",
        "priority": "u=1, i",
        "referer": "https://cafebazaar.ir/",
        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    all_apps = []

    # Stage 1: Fetch the first page using GetPageV2Request
    offset = 0
    apps, offset = fetch_initial_page(api_url_v2, headers, subcategory_path)
    all_apps.extend(apps)

    # Stage 2: Fetch subsequent pages using GetPageBodyRequest and offset
    while offset is not None:
        apps, offset = fetch_next_page(api_url_body, headers, subcategory_path, offset)
        all_apps.extend(apps)

        # Add a small random delay between requests
        time.sleep(random.uniform(0.5, 1.0))

    return all_apps


# Fetch the initial page using GetPageV2Request
def fetch_initial_page(api_url_v2, headers, subcategory_path):
    payload = {
        "properties": {
            "language": 2,
            "clientID": config.DEVICE_ID,
            "deviceID": config.DEVICE_ID,
            "clientVersion": "web"
        },
        "singleRequest": {
            "getPageV2Request": {
                "path": subcategory_path,
                "offset": 0
            }
        }
    }

    try:
        session = get_session()
        response = session.post(api_url_v2, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            apps = extract_apps(data)

            # Assuming the offset for the next request can be inferred from the number of apps returned
            if len(apps) > 0:
                return apps, len(apps)  # Return the number of apps as the offset
            else:
                return apps, None  # No more apps, end the loop
        else:
            print(f"Failed to fetch data from initial request, status code: {response.status_code}")
            return [], None
    except Exception as e:
        print(f"Error fetching initial page: {e}")
        return [], None


# Fetch the next page using GetPageBodyRequest
def fetch_next_page(api_url_body, headers, subcategory_path, offset):
    payload = {
        "properties": {
            "language": 2,
            "clientID": config.DEVICE_ID,
            "deviceID": config.DEVICE_ID,
            "clientVersion": "web"
        },
        "singleRequest": {
            "getPageBodyRequest": {
                "path": subcategory_path,
                "offset": offset
            }
        }
    }

    try:
        session = get_session()
        response = session.post(api_url_body, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            apps = extract_apps_from_page_request(data)

            # If there are more apps to fetch, increment the offset
            if len(apps) > 0:
                return apps, offset + len(apps)
            else:
                return apps, None  # No more apps to fetch, end pagination
        else:
            print(f"Failed to fetch data from next page, status code: {response.status_code}")
            return [], None
    except Exception as e:
        print(f"Error fetching next page: {e}")
        return [], None


def extract_apps(response_data):
    # Extract relevant app information from 'pageBodyInfo -> pageBody -> rows'
    apps = []
    rows = response_data.get('singleReply', {}).get('getPageV2Reply', {}).get('page', {}).get('pageBodyInfo', {}).get(
        'pageBody', {}).get('rows', [])

    for row in rows:
        if 'simpleAppItem' in row and 'info' in row['simpleAppItem']:
            apps.append(row['simpleAppItem']['info'])
    return apps


def extract_apps_from_page_request(response_data):
    # Extract relevant app information from 'pageBodyInfo -> pageBody -> rows'
    apps = []
    rows = response_data.get('singleReply', {}).get('getPageBodyReply', {}).get('pageBody', {}).get('rows', [])

    for row in rows:
        if 'simpleAppItem' in row and 'info' in row['simpleAppItem']:
            apps.append(row['simpleAppItem']['info'])
    return apps


def fetch_app_details(package_name, subcategory):
    api_url = "https://api.cafebazaar.ir/rest-v1/process/AppDetailsV2Request"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://cafebazaar.ir",
        "priority": "u=1, i",
        "referer": "https://cafebazaar.ir/",
        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    # Create the payload for the request
    payload = {
        "properties": {
            "language": 2,
            "clientID": config.DEVICE_ID,
            "deviceID": config.DEVICE_ID,
            "clientVersion": "web"
        },
        "singleRequest": {
            "appDetailsV2Request": {
                "packageName": package_name
            }
        }
    }

    # Make the API request with retry and error handling
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            session = get_session()
            response = session.post(api_url, headers=headers, json=payload, timeout=30, verify=True)

            # Check if the response was successful
            if response.status_code == 200:
                return extract_app_details(response.json(), subcategory)
            else:
                print(f"Failed to fetch data, status code: {response.status_code}, attempt {attempt + 1}/{max_retries}")

        except requests.exceptions.SSLError as ssl_err:
            print(f"SSL error on attempt {attempt + 1}/{max_retries}: {ssl_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error on attempt {attempt + 1}/{max_retries}: {req_err}")
        except Exception as err:
            print(f"Unexpected error on attempt {attempt + 1}/{max_retries}: {err}")

        # Only sleep if we're going to retry
        if attempt < max_retries - 1:
            # Exponential backoff with jitter
            sleep_time = retry_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

    print(f"Failed to fetch details for {package_name} after {max_retries} attempts")
    return None


def extract_app_details(app_data, subcategory):
    reply = app_data.get('singleReply', {}).get('appDetailsV2Reply', {})
    tags = [
        tag.get('title')
        for tag in reply.get('meta', {}).get('tags', [])
        if tag.get('title')
    ]
    app_from_dict = AppDetails.from_dict(reply, Source.BAZAR, tags, subcategory)
    app_from_dict.save_to_db(config.RESULT_FILE)
    return app_from_dict
