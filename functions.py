from bs4 import BeautifulSoup
import requests
import re
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from typing import Optional, Set, Union, List

# Regex pattern used for finding all string that might represent phone numbers
REGEX_NUMBER_WIDE = r"[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\.\0-9]*(?=[^0-9])"


def make_soup(url: str):
    """
    Fetch content from the given URL and parse it using BeautifulSoup.

    Parameters:
    - url (str): The targeted URL to fetch content from.

    Returns:
    - BeautifulSoup object if successful.
    - None if there was an exception during the request.
    """
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, 'html5lib')
        return (soup)
    except requests.exceptions.RequestException as e:
        print("missing url", e, file=sys.stderr)
        return ""


def get_numbers(soup: BeautifulSoup) -> Optional[List[str]]:
    """
    Extract phone numbers from the give BeautifulSoup object.

    Parameters:
    - soup (str): The soup object to extract phone numbers from.

    Returns:
    - List of extracted phone numbers.
    - None if no phone numbers are found.

    Notes:
    - Phone numbers are identified based on the REGEX_NUMBER_WIDE pattern defined outside of the function.
    - Numbers are cleaned and filtered to ensure they adhere to the E.164 format criteria.
    - Certain patterns, like those of dates and years, are excluded to reduce false positives.
    """

    # Extract text from soup
    soup_text = soup.get_text()

    # Cast a wide net to find all potential number that could satisfy conditions
    potential_numbers = re.findall(REGEX_NUMBER_WIDE, soup_text)

    # Filter and process the numbers in one step
    phone_numbers = []
    for number in potential_numbers:
        cleaned_num = number.strip().replace("  ", "").replace("\xa0", "-")

        # Skip candidates matching date format (xxxx-xx-xx)
        if re.match(r'\b\d{4}-\d{2}-\d{2}\b', cleaned_num):
            continue

        # Split on newline and process each part
        parts = cleaned_num.split('\n')
        for part in parts:
            # Ensure there are between 6 to 15 digits in the string (in accoradnce with E.164)
            if not 6 <= len(re.findall(r'\d', part)) <= 15:
                continue

            # Strip characters
            part = part.strip('.,').rstrip('( ')

            # Replace hyphens and backslash with whitespace
            part = part.replace("-", " ").replace("/", " ")

            # Remove doublespace
            part = re.sub(r'\s\s+', '', part)

            # Ensure the string contains only characters found in phone numbers (0-9," ", (),-,\)
            if re.search(r'[^0-9+\s\(\)-]', part):
                continue

            # Ensure there's at least one non-digit character (eliminates SSN, OIB, Area Codes...)
            if not re.search(r'\D', part):
                continue

            # Skip strings that start with five or more digits (eliminates misc scraped numbers)
            if re.match(r'^\d{5,}', part):
                continue

            # Skip strings that start with three or four numbers where the first is between 1 and 9 (eliminates years but not 0800 numbers)
            if re.match(r'^[1-9]\d{2,3}', part):
                continue

            phone_numbers.append(part)

    # Remove duplicates
    unique_phone_numbers = remove_duplicates(phone_numbers)

    return unique_phone_numbers if unique_phone_numbers else None


def remove_duplicates(input_list: List[str]) -> List[str]:
    """
    Removes duplicate phone numbers that creating a set won't identify


    Parameters:
    - input_list (List[str]): The list of strings from which to remove duplicates.

    Returns:
    - List[str]: A list of unique strings with duplicates removed.

    """

    seen = set()  # A set to keep track of seen strings
    output_list = []  # The output list that will contain unique strings

    for item in input_list:
        cleaned_item = re.sub(r'\D', '', item)  # Remove non digit characters

        # If the cleaned item is not in the seen set, add it to the output list and the seen set
        if cleaned_item not in seen:
            seen.add(cleaned_item)
            # Add the original item to the output list
            output_list.append(item)

    return output_list


def find_logo(soup: BeautifulSoup) -> Optional[str]:
    """
    Searches for the URL of a website's logo within the provided BeautifulSoup object.

    This function looks for the logo by checking common attributes and values within 
    the website's HTML content, such as "class", "src", "id", and "alt". It also 
    checks for common aliases of logos like "logo", "brand", "site", etc.

    Parameters:
    - soup (BeautifulSoup): The BeautifulSoup object containing the parsed web page.

    Returns:
    - str: The URL of the logo if found, otherwise returns None.

    Notes:
    - Returned URL can be global or local.
    """

    # Compile the regular expression pattern for image file extensions
    is_photo_pattern = re.compile(r'\.(jpg|png|svg)$', re.I)

    # Define potential attributes and values to search for
    hiding_place = ["class", "src", "id", "alt"]
    alliases = ["logo", "brand", "site", "company", "name"]

    # Search for the logo using the defined attributes and values
    for place in hiding_place:
        for alias in alliases:
            logo = soup.find("img", {place: re.compile(alias, re.I)})

            # If a potential logo is found and has a valid image URL, return the URL
            if logo and 'src' in logo.attrs and is_photo_pattern.search(logo['src']):
                return logo['src']

    # If no logo is found, return None
    return None


def return_logo_url(logo: str, url: str) -> str:
    """
    Return a full URL for the given logo. If the logo already has a domain, it's returned as-is.
    Otherwise, it's combined with the domain from the provided URL.

    Parameters:
    - logo (str): The logo's URL, which might be absolute or relative.
    - url (str): The base URL to combine with the logo if the logo is a relative path.

    Returns:
    - str: The full URL for the logo.
    """
    parsed_url = urlparse(url)
    parsed_logo = urlparse(logo)

    if bool(parsed_logo.netloc):
        return logo
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # Checks for "//"
    if not base_url.endswith('/') and not logo.startswith('/'):
        base_url += '/'
    return base_url + logo
