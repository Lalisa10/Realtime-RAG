import requests
from xml.etree import ElementTree
import asyncio
import json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"}

def get_urls(sitemap_url):
    try:
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()

        root = ElementTree.fromstring(response.content)

        namespace = {"ns" : "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        return urls
    except Exception as e:
        print(f"Error fetching sitemap {e}")
        return []

def get_product_urls(sitemap_url, max_pages_number = None):
    page_urls = get_urls(sitemap_url)

    if max_pages_number is not None and max_pages_number < len(page_urls):
        page_urls = page_urls[:max_pages_number]

    result = []
    for page_url in page_urls:
        product_urls = get_urls(page_url)
        result.extend(product_urls)
    return result

if __name__ == "__main__":
    sitemap_url = 'https://tiki.vn/clover/sitemap/product_master'
    product_urls = get_product_urls(sitemap_url=sitemap_url)
    with open("data/products_url.json", "w", encoding="utf-8") as f:
        json.dump(product_urls, f, ensure_ascii=False, indent=2)
    