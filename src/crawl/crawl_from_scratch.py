from src.crawl.url import get_product_urls
from src.crawl.product_scraper import crawl_multiple_urls
import json
from datetime import datetime
import asyncio

async def run_crawl(urls):    
    print(f"Bắt đầu crawl {len(urls)} URLs lúc {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    await crawl_multiple_urls(urls, max_concurrent=5)

def main():
    with open('data/products_url.json', 'r', encoding='utf-8') as f:
        product_urls = json.load(fp=f)
    asyncio.run(run_crawl(product_urls[:100]))
    

if __name__ == "__main__":
    main()