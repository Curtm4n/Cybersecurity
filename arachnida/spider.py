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
            #print("Valid URL !")
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
        #print(f"{path} folder already exist")
    return True

"""def valid_img_url(url):
    url_with_http_scheme = urlparse(url)._replace(scheme='http').geturl()
    print(url_with_http_scheme)
    return url_with_http_scheme.startswith('http')"""

def download_img(url, path):
    print(f"downloading img at url: {url}, into {path}")

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
        
        #if (img_url and valid_img_url(img_url)):
        if (img_url):
            img_url = urljoin(url, img_url)
            img_name = os.path.basename(urlparse(img_url).path)
            print(img_name)
            if not img_name.lower().endswith(valid_ext):
                continue
            img_path = os.path.join(path, img_name)
            if img_url not in downloaded_images:
                download_img(img_url, img_path)
                downloaded_images.add(img_url)


def main():
    downloaded_images = set()
    args = get_args()
    response = check_url(args.URL)
    if response is None:
        return
    domain_base = tldextract.extract(args.URL).domain
    #print(f"The base of the domain is: {domain_base}")
    args.path = os.path.abspath(os.path.expanduser(args.path))
    if not check_path(args.path):
        print("error with the path")
        return
    get_imgs(response, args.URL, args.path, downloaded_images)

if __name__ == "__main__":
    main()