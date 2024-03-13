import requests
from bs4 import BeautifulSoup
import regex as re
from urllib.parse import urlsplit
import socket
from urllib3.exceptions import ProtocolError

def get_unique_urls(url, visited_urls):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        reqs = requests.get(url, headers=headers)
        reqs.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.ConnectionError):
            if hasattr(e, 'args') and e.args and isinstance(e.args[0], ProtocolError) and isinstance(e.args[0].args[0], socket.gaierror) and e.args[0].args[0].errno == 11001:
                print(f"Error resolving hostname {url}: {e}")
            else:
                print(f"Error making the request to {url}: {e}")
        elif isinstance(e, requests.exceptions.HTTPError):
            print(f"HTTP error occurred while making the request to {url}: {e}")
        elif isinstance(e, ProtocolError):
            print(f"ProtocolError occurred while making the request to {url}: {e}")
        else:
            print(f"Other RequestException occurred: {e}")
        return [url]

    print(f"URL ---> {url}")

    if reqs.status_code == 200:
        try:
            soup = BeautifulSoup(reqs.text, 'html.parser', from_encoding='utf-8')
        except Exception as e:
            print(f"Error parsing the HTML content: {e}")
            return [url]

        urls = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href not in urls and url in href and href not in visited_urls:
                urls.append(href)
                visited_urls.add(href)

                small_list = []  # Separate list for each level
                try:
                    sub_reqs = requests.get(href, headers=headers)
                    sub_reqs.raise_for_status()
                    sub_soup = BeautifulSoup(sub_reqs.text, 'html.parser', from_encoding='utf-8')
                except requests.exceptions.RequestException as e:
                    if isinstance(e, requests.exceptions.ConnectionError):
                        if hasattr(e, 'args') and e.args and isinstance(e.args[0], ProtocolError) and isinstance(e.args[0].args[0], socket.gaierror) and e.args[0].args[0].errno == 11001:
                            print(f"Error resolving hostname {href}: {e}")
                        else:
                            print(f"Error making the sub-request to {href}: {e}")
                    continue

                for sub_link in sub_soup.find_all('a'):
                    sub_href = sub_link.get('href')
                    if sub_href and sub_href not in small_list and url in sub_href and sub_href not in visited_urls:
                        small_list.append(sub_href)
                        visited_urls.add(sub_href)

                        try:
                            so_sub_reqs = requests.get(sub_href, headers=headers)
                            so_sub_reqs.raise_for_status()
                            so_sub_soup = BeautifulSoup(so_sub_reqs.text, 'html.parser', from_encoding='utf-8')
                        except requests.exceptions.RequestException as e:
                            if isinstance(e, requests.exceptions.ConnectionError):
                                if hasattr(e, 'args') and e.args and isinstance(e.args[0], ProtocolError) and isinstance(e.args[0].args[0], socket.gaierror) and e.args[0].args[0].errno == 11001:
                                    print(f"Error resolving hostname {so_sub_href}: {e}")
                                else:
                                    print(f"Error making the sub-sub-request to {so_sub_href}: {e}")
                            continue

                        for so_sub_link in so_sub_soup.find_all('a'):
                            so_sub_href = so_sub_link.get('href')
                            if so_sub_href and so_sub_href not in small_list and sub_href in so_sub_href and so_sub_href not in visited_urls:
                                small_list.append(so_sub_href)
                                visited_urls.add(so_sub_href)

                urls.extend(small_list)  # Extend the main list with the small_list

        print(f"URL ---> {url} ---> extracted {len(urls)} urls")  # Print the total number of URLs extracted
        return list(set(urls))

    else:
        print(f"Failed to retrieve the page. Status code: {reqs.status_code}")
        return [url]

# The rest of your code remains unchanged




def get_home_page_url(url):
    url_components = urlsplit(url)
    return f"{url_components.scheme}://{url_components.netloc}"

