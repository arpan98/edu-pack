import argparse
import json
import itertools
import re
import os
import sys
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

from PIL import Image


REQUEST_HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}

def remove_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im

def get_soup(url, header):
    response = urlopen(Request(url, headers=header))
    return BeautifulSoup(response, 'html.parser')

def get_query_url(query):
    return "https://www.google.co.in/search?q=%s&source=lnms&tbm=isch" % query

def extract_images_from_soup(soup):
    image_elements = soup.find_all("div", {"class": "rg_meta"})
    metadata_dicts = (json.loads(e.text) for e in image_elements)
    link_type_records = ((d["ou"], d["ity"]) for d in metadata_dicts)
    return link_type_records

def extract_images(query, num_images):
    url = get_query_url(query)
    soup = get_soup(url, REQUEST_HEADER)
    link_type_records = extract_images_from_soup(soup)
    return itertools.islice(link_type_records, num_images)

def get_raw_image(url):
    req = Request(url, headers=REQUEST_HEADER)
    resp = urlopen(req)
    return resp.read()

def save_image(raw_image, image_type, save_directory, uid, image_number):
    extension = image_type if image_type else 'jpg'
    # extension = 'jpg'
    file_name = str(uid) + "_image_" + str(image_number) + "." + extension
    save_path = os.path.join(save_directory, file_name)
    with open(save_path, 'wb') as image_file:
        image_file.write(raw_image)
    if extension == 'png':
        im = Image.open(save_path)
        im = remove_transparency(im)
        im.save(save_path)
    return save_path

def download_images_to_dir(images, save_directory, num_images, uid, im_num):
    for i, (url, image_type) in enumerate(images):
        try:
            raw_image = get_raw_image(url)
            return save_image(raw_image, image_type, save_directory, uid, im_num)
        except Exception as e:
            print(e)

def run(query, im_num, save_directory="images/", num_images=1, uid=0):
    query = '+'.join(query.split())
    print("Extracting image links")
    images = extract_images(query, num_images)
    print("Downloading images")
    savepath = download_images_to_dir(images, save_directory, num_images, uid, im_num)
    print("Finished")
    return savepath

def main():
    parser = argparse.ArgumentParser(description='Scrape Google images')
    parser.add_argument('-s', '--search', default='bananas', type=str, help='search term')
    parser.add_argument('-i', '--id', default=0, type=int, help='unique id')
    parser.add_argument('-k', '--im_num', default=0, type=int, help='image number')
    parser.add_argument('-n', '--num_images', default=1, type=int, help='num images to save')
    parser.add_argument('-d', '--directory', default='images/', type=str, help='save directory')
    args = parser.parse_args()
    run(args.search, args.im_num, args.directory, args.num_images, args.id)

if __name__ == '__main__':
    main()