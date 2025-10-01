#!/usr/bin/env python3

import argparse, requests, tldextract, os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def get_args():
    parser = argparse.ArgumentParser(description="Spider is a little web crawler that download images recursively from a website")
    parser.add_argument("URL", help="URL of the website you want to download images from")
    parser.add_argument("-r", "--recursive", help="recursively downloads the images in a URL received as a parameter", action="store_true")
    parser.add_argument("-l", "--level", help="maximum depth level of recursive download", type=int, nargs="?", const=5, default=None, metavar="N")
    parser.add_argument("-p", "--path", help="indicates the path where the downloaded files will be saved, ./data/ by default", nargs="?", const="./data/", default="./data/")
    args = parser.parse_args()
    if args.level is not None and not args.recursive:
        parser.error("option -l/--level require -r/--recursive.")
    if args.recursive:
        if args.level is None:
            args.level = 5
    args.path = os.path.abspath(os.path.expanduser(args.path))
    
    #VERBOSE PART FOR THE ARGUMENTS, CAN BE COMMENTED
    """    print("The download will be recursive")
        print(f"The max depth level of the recursive download will be of {args.level}")
    print(f"This is the URL you entered: {args.URL}\nData will be saved here: {args.path}")"""
    
    return args

def check_url(url):
    #headers meant for bypassing 403 forbidden on sites with basic script/scrapping protection (doesn't work on most sites)
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response
        else:
            print(f"Error status: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"bad URL or inacessible: {e}")
        return None

def check_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"directory {path} has been created successfully")
        except OSError as e:
            print(f"Error while creating {path} directory: {e}")
            return False
    else:
        if not os.path.isdir(path):
            print(f"{path} already exist as a file cannot create a folder of the same name")
            return False
    return True

def download_img(url, path):
    #print(f"downloading img at url: {url}, into {path}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"✅ successfully downloaded image {url}")
        else:
            print(f"❌ Error downloading image {url}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error while getting image {url}")

def get_imgs(response, url, path, downloaded_images):
    valid_ext = (".jpg", ".jpeg", ".png", ".gif", ".bmp")
    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img") + soup.find_all("picture")

    for img in img_tags:
        if img.name == "picture":
            source_tag = img.find("source")
            if source_tag:
                img_url = source_tag.get("srcset", "").split()[0]
            else:
                img_url = img.get("src")
        else:
            img_url = img.get("src")
        
        if (img_url):
            img_url = urljoin(url, img_url)
            img_name = os.path.basename(urlparse(img_url).path)
            if not img_name.lower().endswith(valid_ext):
                continue
            img_path = os.path.join(path, img_name)
            if img_url not in downloaded_images:
                download_img(img_url, img_path)
                downloaded_images.add(img_url)

def get_domain_name(url):
    domain_base = tldextract.extract(url).domain
    parsed_url = urlparse(url)
    port = parsed_url.port
    if port:
        domain_base = f"{domain_base}:{port}"
    #print(f"The base of the domain is: {domain_base}")
    return domain_base

def crawler(response, url, path, level, downloaded_images, visited_sites):
    print(f"We enter crawler fonction, we are level {level} on url {url}")
    if level == 0:
        return
    if url in visited_sites and visited_sites[url] >= level:
        print(f"We already visited site {url} with a level of {visited_sites[url]}")
        return
    if not url in visited_sites:
        get_imgs(response, url, path, downloaded_images)
        visited_sites[url] = level
        print("These are the sites already visited : ")
        for site in visited_sites:
            print(site)
    visited_sites[url] = level

    domain_name = get_domain_name(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    for link in links:
        href = link.get("href")
        if href:
            next_url = urljoin(url, href)
            if next_url == url or next_url.startswith(url + "#"):
                print(f"URL {next_url} is either the same we curently on or is an anchor we skip")
                continue
            link_domain = get_domain_name(next_url)
            if link_domain == domain_name:
                print(f"We're going on link {next_url}")
                response = check_url(next_url)
                if response is None:
                    continue
                crawler(response, next_url, path, level - 1, downloaded_images, visited_sites)
            else:
                print(f"We ignore link {next_url}")

def main():
    downloaded_images = set()
    visited_sites = {}
    args = get_args()
    response = check_url(args.URL)
    if response is None:
        exit(1)
    if not check_path(args.path):
        exit(1)
    if args.recursive:
        crawler(response, args.URL, args.path, args.level, downloaded_images, visited_sites)
    else:
        get_imgs(response, args.URL, args.path, downloaded_images)

if __name__ == "__main__":
    main()