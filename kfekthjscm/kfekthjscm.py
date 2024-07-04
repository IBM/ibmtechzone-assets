import os
import re
import json
import asyncio
from urllib.parse import urlparse, urlunparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

def is_allowed_file(link):
    """Check if the link points to a skippable file type."""
    allowed_extensions = ('.html', '.htm')
    return link.lower().endswith(allowed_extensions)

def get_path_segment(href):
    """Extract the part of the href after the domain and before the next slash."""
    parsed_url = urlparse(href)
    path = parsed_url.path
    if path.startswith('/'):
        path_segments = path.split('/')
        if len(path_segments) > 1:
            return f"/{path_segments[1]}/"
    return None

def should_add_link(href, domain_routes):
    """Check if the href should be added based on the domain routes."""
    path_segment = get_path_segment(href)
    if path_segment:
        return any(path_segment.startswith(route) for route in domain_routes)
    return False

def strip_fragment(url):
    """Remove the fragment from the URL."""
    parsed_url = urlparse(url)
    return urlunparse(parsed_url._replace(fragment=''))

def sort_data_points(mast_dict, reverse=False):
    """Sort the dictionary mast_dict based on the alphabetical order of the links.

    Args:
        mast_dict (dict): The dictionary containing 'url_text' and 'links'.
        reverse (bool, optional): If True, sort in descending order. Defaults to False.

    Returns:
        dict: The sorted dictionary.
    """
    # Check if both url_text and links are present and have the same length
    if "url_text" not in mast_dict or "links" not in mast_dict:
        return mast_dict  # Return the original dictionary if keys are missing
    
    if not mast_dict["url_text"] or not mast_dict["links"]:
        return mast_dict  # Return the original dictionary if lists are empty

    if len(mast_dict["url_text"]) != len(mast_dict["links"]):
        raise ValueError("'url_text' and 'links' must have the same length.")
    
    # Zip the url_text and links together
    combined = list(zip(mast_dict["url_text"], mast_dict["links"]))
    
    if not combined:
        return mast_dict  # If there is nothing to sort, return the original dictionary
    
    # Sort the combined list by the links (second element of the tuple)
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=reverse)
    
    # Unzip the sorted combined list
    mast_dict["url_text"], mast_dict["links"] = zip(*sorted_combined)

    # Convert the tuples back to lists
    mast_dict["url_text"] = list(mast_dict["url_text"])
    mast_dict["links"] = list(mast_dict["links"])

    return mast_dict

def clean_data_points(mast_dict, processed_dict):
    """ Cleans the dictionary

    Args:
        mast_dict (dict): dictionary to be cleaned

    Returns:
        dict: cleaned dictionary
    """
    link_indices_to_remove = []
    text_indices_to_remove = []

    for index, url_link in enumerate(mast_dict["links"]):
        if any(url_link in links for links in [mast_dict["error_links"], mast_dict["forbidden_links"], mast_dict["flagged_links"], processed_dict["processed_links"]]):
            link_indices_to_remove.append(index)
    
    for index in sorted(link_indices_to_remove, reverse=True):
        mast_dict["links"].pop(index)

    for index, url_text in enumerate(mast_dict["url_text"]):
        if url_text in processed_dict["url_text"]:
            text_indices_to_remove.append(index)
    
    for index in sorted(text_indices_to_remove, reverse=True):
        mast_dict["url_text"].pop(index)
    
    return mast_dict


def load_existing_data(filename, ext, data_type):
    """Load existing data if it exists, otherwise return a new one."""
    if data_type == 'processed':
        filepath = f'processed/{filename}_links.{ext}'
    elif data_type == 'output':
        filepath = f'output/{filename}_crawled.{ext}'
    else:
        filepath = f'mast_dict/{filename}_dict.{ext}'

    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, KeyError):
            # Handle the case where the file is empty or not properly formatted
            if data_type == 'mast_dict':
                return {
                    "url_text": [],
                    "links": [],
                    "error_links": [],
                    "forbidden_links": [],
                    "flagged_links": []
                }
            elif data_type == 'processed':
                return {
                    "url_text": [],
                    "processed_links": [],
                }
            else:
                return []
    else:
        if data_type == 'mast_dict':
            return {
                "url_text": [],
                "links": [],
                "error_links": [],
                "forbidden_links": [],
                "flagged_links": []
            }
        elif data_type == 'processed':
            return {
                "url_text": [],
                "processed_links": []
            }
        else:
            return []

def is_page_data_exists(scraped_data, url):
    """Check if page data for a given URL already exists in the scraped data."""
    return any(page['url'] == url for page in scraped_data)

async def extract_links(page, domain_url, mast_dict, filename, ext, domain_routes = None):
    """ Extract the links and their respective names from a page.

    Args:
        page (_type_): Page to be crawled
        domain_url (_type_): domain url for relative path
        mast_dict (_type_): master dictionary to store the links and name
        filename (_type_): filename to store the master dictionary

    Returns:
        dict: Returns a dictionary of all the links that are available on that page along with their names.
    """
    # Get all the list items
    list_items = await page.query_selector_all('li')

    # Iterate through each list item
    for item in list_items:
        # Get the anchor tag within the list item
        anchor = await item.query_selector('a')

        if anchor:
            sub_link = None
            # Extract the link URL using get_attribute('href')
            href = await anchor.get_attribute('href')
            onclick_value = await anchor.get_attribute('onclick')
            # Check if the website has a dynamic link attached.
            if not str(href).startswith("javascript:void(0)"):
                text = await anchor.inner_text()

                if str(href).startswith(domain_url):
                    if href not in mast_dict["links"]:
                        if domain_routes is not None:
                            if should_add_link(href, domain_routes):
                                mast_dict["links"].append(href)
                                mast_dict["url_text"].append(text)
                        else:    
                            mast_dict["links"].append(href)
                            mast_dict["url_text"].append(text)

                elif str(href).startswith("/"):
                    href_link = domain_url + href
                    if href_link not in mast_dict["links"]:
                        if domain_routes is not None:
                            if should_add_link(href_link, domain_routes):
                                mast_dict["links"].append(href_link)
                                mast_dict["url_text"].append(text)
                        else:
                            mast_dict["links"].append(href_link)
                            mast_dict["url_text"].append(text)
                
                else:
                    continue

            elif onclick_value:
                text = await anchor.inner_text()
                # Check if text already exists in the database to avoid duplicate links.
                # if text not in mast_dict["url_text"]:
                # Use regex to extract the first parameter between parentheses
                match = re.search(r"\('(\/.*?)'", onclick_value)
                if match:
                    sub_link = match.group(1)
                    if str(sub_link).startswith(".."):
                        continue
                    # Construct the full URL if it's relative
                    elif not str(sub_link).startswith('https://'):
                        sub_link_url = domain_url + sub_link
                        if sub_link_url not in mast_dict["links"]:
                            if domain_routes:
                                if should_add_link(sub_link_url, domain_routes):
                                    mast_dict["links"].append(sub_link_url)
                                    mast_dict["url_text"].append(text)
                            else:
                                mast_dict["links"].append(sub_link_url)
                                mast_dict["url_text"].append(text)
                    else:
                        if sub_link not in mast_dict["links"]:
                            if domain_routes:
                                if should_add_link(sub_link, domain_routes):
                                    mast_dict["links"].append(sub_link)
                                    mast_dict["url_text"].append(text)
                            else:
                                mast_dict["links"].append(sub_link)
                                mast_dict["url_text"].append(text)


    with open(f'mast_dict/{filename}_dict.{ext}', 'w', encoding='utf-8') as f:
        json.dump(mast_dict, f, ensure_ascii=False, indent=2)

    return mast_dict

async def extract_links_with_name(page, domain_url = ''):
    # Get all the list items
    list_items = await page.query_selector_all('li')

    links = []

    # Iterate through each list item
    for item in list_items:
        # Get the anchor tag within the list item
        anchor = await item.query_selector('a')

        if anchor:
            # Extract the link URL using get_attribute('href')
            href = await anchor.get_attribute('href')
            sub_link = None
            onclick_value = await anchor.get_attribute('onclick')
            
            if onclick_value:
                # Use regex to extract the first parameter between parentheses
                match = re.search(r"\('(\/.*?)'", onclick_value)
                if match:
                    sub_link = match.group(1)
                    # Construct the full URL if it's relative
                    if sub_link.startswith('/'):
                        sub_link = domain_url + sub_link

            # Extract the link text using inner_text()
            text = await anchor.inner_text()
            links.append({"text": text, "href": href, "sub_link": sub_link})

    return links

async def process_single_link(page, link, mast_dict, processed_dict, scraped_data, filename, ext, domain_url, domain_routes, reprocess=False):
    # Strip fragment identifier from the link
    """Process a single link."""
    clean_link = strip_fragment(link)

    if not is_allowed_file(clean_link):
        print(f"Skipping processing of skippable file type: {clean_link}")
        if reprocess:
            return False, processed_dict, mast_dict, scraped_data
        else:
            index = mast_dict['links'].index(link)
            mast_dict["links"].pop(index)
            mast_dict["url_text"].pop(index)

        return False, processed_dict, mast_dict, scraped_data
    
    try:
        print(f"Processing: {link}")
        
        # Retry mechanism for navigation
        response_info = None
        attempt = 0
        max_attempts = 3

        while response_info is None and attempt < max_attempts:
            try:
                response_info = await page.goto(clean_link)
                if response_info is None:
                    print(f"Navigation attempt {attempt + 1} returned null. Retrying...")
                    attempt += 1
                else:
                    print(f"Navigation successful. Status: {response_info.status}")
            except PlaywrightTimeoutError as e:
                print(f"Navigation attempt {attempt + 1} timed out: {e}")
                attempt += 1

        if response_info and response_info.status == 200:
            mast_dict = await extract_links(page, domain_url, mast_dict, filename, ext, domain_routes)
            page_data = {
                'url': clean_link,
                'title': await page.title(),
                'text': await page.evaluate("document.body.innerText"),
                'images': await page.evaluate("Array.from(document.querySelectorAll('img')).map(img => img.src)"),
                # 'links': await extract_links_with_name(page, domain_url),
                # 'forms': await page.evaluate("Array.from(document.querySelectorAll('form')).map(form => { let formData = {}; Array.from(form.elements).forEach(input => formData[input.name] = input.value); return formData; })")
            }

            # Add page data if it does not already exist
            if not is_page_data_exists(scraped_data, clean_link):
                scraped_data.append(page_data)

            if link not in processed_dict["processed_links"]:
                if reprocess:
                    index = mast_dict['flagged_links'].index(link)
                    mast_dict["flagged_links"].pop(index)
                    processed_dict["processed_links"].append(link)
                else:
                    index = mast_dict['links'].index(link)
                    mast_dict["links"].pop(index)
                    url_text = mast_dict["url_text"].pop(index)
                    processed_dict["processed_links"].append(link)
                    processed_dict["url_text"].append(url_text)
            
            else:
                if reprocess:
                    mast_dict["flagged_links"].remove(link)
                else:
                    index = mast_dict['links'].index(link)
                    mast_dict["links"].pop(index)
                    mast_dict["url_text"].pop(index)
                

        elif response_info and response_info.status == 403:
            if link not in mast_dict['forbidden_links']:
                if reprocess:
                    mast_dict['flagged_links'].remove(link)
                    mast_dict['forbidden_links'].append(link)
                    
                else:
                    index = mast_dict['links'].index(link)
                    mast_dict["links"].pop(index)
                    mast_dict["url_text"].pop(index)
                    mast_dict['forbidden_links'].append(link)
                    


        elif response_info and response_info.status == 404:
            if link not in mast_dict['error_links']:
                if reprocess:
                    mast_dict['flagged_links'].remove(link)
                    mast_dict['error_links'].append(link)
                    
                else:
                    index = mast_dict['links'].index(link)
                    mast_dict["links"].pop(index)
                    mast_dict["url_text"].pop(index)
                    mast_dict['error_links'].append(link)


        return True, processed_dict, mast_dict, scraped_data  # Successfully processed

    except Exception as e:
        print(f"Failed to navigate to {link}: {e}")
        return False, processed_dict, mast_dict, scraped_data  # Failed to process

async def process_links(page, mast_dict, processed_dict, scraped_data, filename, ext, domain_url, domain_routes):
    """Process the links in mast_dict."""
    i = 0
    while i < len(mast_dict["links"]):
        link = mast_dict["links"][i]
        clean_link = strip_fragment(link)
        if (link not in processed_dict["processed_links"]) or (link in processed_dict["processed_links"] and not is_page_data_exists(scraped_data,clean_link)):
            success, processed_dict, mast_dict, scraped_data = await process_single_link(page, link, mast_dict, processed_dict, scraped_data, filename, ext, domain_url, domain_routes)
            if success:
                i = 0  # Restart from the beginning if successfully processed
            else:
                if link not in mast_dict['flagged_links']:
                    mast_dict['flagged_links'].append(link)
                i += 1  # Move to the next link if failed

        else:
            print(link)
            mast_dict["links"].remove(link)
            i += 1

        # Save the scraped data to a JSON file
        with open(f"output/{filename}_crawled.{ext}", 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)

        # Save the processed links to a JSON file
        with open(f"processed/{filename}_links.{ext}", 'w', encoding='utf-8') as f:
            json.dump(processed_dict, f, ensure_ascii=False, indent=2)

    return mast_dict, scraped_data, processed_dict

async def reprocess_flagged_links(page, mast_dict, processed_dict, scraped_data, filename, ext, domain_url, domain_routes):
    """Reprocess the flagged links."""

    i = 0
    new_flagged_links = []
    for link in mast_dict['flagged_links']:
        if link not in processed_dict["processed_links"]:
            success, processed_dict, mast_dict, scraped_data = await process_single_link(page, link, mast_dict, processed_dict, scraped_data, filename, ext, domain_url, domain_routes, reprocess=True)
            if success:
                url_text = mast_dict["url_text"][i]
                processed_dict["url_text"].append(url_text)
                i+=1
            else:
                new_flagged_links.append(link)

    mast_dict['flagged_links'] = new_flagged_links

    # Save the scraped data to a JSON file
    with open(f"output/{filename}_crawled.{ext}", 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=2)

    # Save the processed links to a JSON file
    with open(f"processed/{filename}_links.{ext}", 'w', encoding='utf-8') as f:
        json.dump(processed_dict, f, ensure_ascii=False, indent=2)

    return mast_dict, scraped_data, processed_dict

async def navigate_and_scrape(root_url, domain_url, filename, ext, domain_routes = None):
    """ Navigates through the provided url to scrape the page

    Args:
        root_url (_type_): url to start the scraping
        domain_url (_type_): domain url for relative path
        filename (_type_): file name to save the crawled data

    Returns:
        dict: Dictionary of all the crawled data.
    """
    mast_dict = load_existing_data(filename, ext, 'mast_dict')
    scraped_data = load_existing_data(filename, ext, 'output')
    processed_dict = load_existing_data(filename, ext, 'processed')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to the root URL first
        await page.goto(root_url)
        
        if root_url not in processed_dict["processed_links"]:
                processed_dict["processed_links"].append(root_url)
                processed_dict["url_text"].append("root_url")
        
        # Get the data from that page
        page_data = {
            'url': root_url,
            'title': await page.title(),
            'text': await page.evaluate("document.body.innerText"),
            'images': await page.evaluate("Array.from(document.querySelectorAll('img')).map(img => img.src)"),
            # 'links': await extract_links_with_name(page, domain_url),
            # 'forms': await page.evaluate("Array.from(document.querySelectorAll('form')).map(form => { let formData = {}; Array.from(form.elements).forEach(input => formData[input.name] = input.value); return formData; })")
        }

        # Add page data if it does not already exist
        if not is_page_data_exists(scraped_data, root_url):
            scraped_data.append(page_data)

        # Extract links from the root URL
        mast_dict = await extract_links(page, domain_url, mast_dict, filename, ext, domain_routes)

        # Process main links
        mast_dict, scraped_data, processed_dict  = await process_links(page, mast_dict, processed_dict, scraped_data, filename, ext, domain_url, domain_routes)

        # Reprocess flagged links
        if mast_dict['flagged_links']:
            print("Reprocessing flagged links...")
            mast_dict, scraped_data, processed_dict = await reprocess_flagged_links(page, mast_dict, processed_dict, scraped_data, filename, ext, domain_url, domain_routes)


        await browser.close()

        clean_mast_dict = clean_data_points(mast_dict, processed_dict)

        with open(f'mast_dict/{filename}_dict.{ext}', 'w', encoding='utf-8') as f:
            json.dump(clean_mast_dict, f, ensure_ascii=False, indent=2)

        return clean_mast_dict, scraped_data


if __name__ == "__main__":
    '''
    This should be the format of each crawl url --> (root_url, domain_url, domain_routes, filename, file_ext) where:

    * root_url is the starting point to crawl the webpage.
    * domain_url is the domain name of the webpage that you want to crawl. Sometimes dynamic webpages give relative path in the onclick function.
    * domain_routes is the route that you want to restrict the crawl to. for example, if /sweets is the route that you want to restrict to, then only links that links that start with domain_url/sweets/... will be crawled. This should be given as a list as this allows for multiple domain routes to be set.
    * filename is the name of the file that you want to log the crawled data.
    * file_ext is the extension in which you want the file to be saved in. For example, json.

    The final format should be something like this -> (root_url, domain_url, domain_routes, filename, file_ext)

    NOTE:
    The crawled output will be available in the output folder with the file having the naming convention of filename_crawled.file_ext.
    You can also monitor the processed links from the processed folder within the file having the naming convention of filename_links.file_ext.
    The flagged links that were excluded from processing is available to monitor in the mast_dict folder within the file filename_dict.file_ext.

    '''
    for folder_name in ["mast_dict","output","processed"]: 
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

    urls = [
    # ("https://www.keisan.nta.go.jp/kyoutu/ky/st/guide/top","https://www.keisan.nta.go.jp","keisan_nta.json"),
    ("https://www.nta.go.jp/taxes/","https://www.nta.go.jp",["/taxes"],"nta_taxes_updated","json")
    # Add more tuples as needed
    ]

    for root_url, domain_url, domain_routes, filename, file_ext in urls:
        # Navigate and scrape the data
        mast_dict, scraped_data = asyncio.run(navigate_and_scrape(root_url, domain_url, filename, file_ext, domain_routes))