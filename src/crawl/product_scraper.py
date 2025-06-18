from playwright.async_api import async_playwright
import random
import json
from asyncio import Semaphore
from bs4 import BeautifulSoup
import asyncio
from src.message_queue.kafka import produce
from src.retrieval.embedding import EmbeddingGenerator
from src.utils.util import load_config

config = load_config('config/config.yaml')
embedding_generator = EmbeddingGenerator(config['embedding']['model'])

def get_embedding(content):
    embedding = embedding_generator.generate(content)
    return embedding

async def crawl_product_info(url, sem, max_retries=3):
    async with sem:
        retryable_status_codes = {404, 429, 500, 502, 503}  # Mã HTTP nên retry
        for attempt in range(max_retries):
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    user_agents = [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
                    ]
                    context = await browser.new_context(
                        user_agent=random.choice(user_agents),
                        viewport={"width": 1280, "height": 4000}
                    )
                    page = await context.new_page()
                    
                    response = await page.goto(url, timeout=30000)
                    if response is None:
                        raise Exception("No response returned from page.goto")

                    # Kiểm tra mã trạng thái HTTP
                    if response.status in retryable_status_codes:
                        raise Exception(f"HTTP Error {response.status} for URL: {url}")
                    elif response.status != 200:
                        # Không retry cho các mã khác (như 403, 401)
                        print(f"Không retry cho HTTP Error {response.status} tại URL: {url}")
                        return {"url": url, "content": f"Lỗi: HTTP Error {response.status}"}

                    await page.wait_for_load_state("domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(3000)

                    html = await page.content()
                    
                    soup = BeautifulSoup(html, "html.parser")
                    
                    title = soup.find("h1", class_="sc-c0f8c612-0 dEurho")
                    if not title:
                        # Lưu HTML để debug nếu không tìm thấy title
                        raise Exception(f"Bị chặn khi truy cập URL: {url}")
                    current_price = soup.find("div", class_="product-price__current-price")
                    original_price = soup.find("div", class_="product-price__original-price")
                    
                    detail_info = soup.find_all("div", class_=lambda x: x and "sc-34e0efdc-3" in x)
                    description = soup.find("div", class_=lambda x: x and ("sc-f5219d7f-0" in x))
                    
                    content = ""
                    content += f"Tiêu đề: {title.get_text(strip=True) if title else 'Không tìm thấy'}\n"
                    content += f"Giá hiện tại: {current_price.get_text(strip=True) if current_price else 'Không tìm thấy'}\n"
                    content += f"Giá gốc: {original_price.get_text(strip=True) if original_price else 'Không tìm thấy'}\n"
                    
                    content += "\nThông tin chi tiết:\n"
                    if detail_info:
                        for info_block in detail_info:
                            spans = info_block.find_all('span')
                            if len(spans) >= 2:
                                key = spans[0].get_text(strip=True)
                                value = spans[1].get_text(strip=True)
                                content += f"{key}: {value}\n"
                    else:
                        content += "Không tìm thấy thông tin chi tiết\n"
                    
                    content += "\nMô tả sản phẩm:\n"
                    description_content = ""
                    if description:
                        tags = description.find_all(["p", "li", "span", "div"])
                        if tags:
                            description_content = "\n".join(tag.get_text(strip=True) for tag in tags if tag.get_text(strip=True))
                        else:
                            description_content = "Không tìm thấy thẻ trong div mô tả"
                    else:
                        description_content = "Không tìm thấy div mô tả"
                    content += description_content
                    
                    content += "\nURL:" + url
                    print(content)
                    embedding = get_embedding(content)
                    record = {
                        "text" : content,
                        "embedding" : embedding
                    }
                    produce('rag_embeddings', json.dumps(record).encode('utf-8'))

                    await context.close()
                    await browser.close()
                    
                    await asyncio.sleep(random.uniform(1, 3))
                    
                    return {"url": url, "content": content.strip()}
            
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Thử lại {url} (lần {attempt + 1}): {str(e)}")
                    await asyncio.sleep(random.uniform(2, 5))
                    continue
                print(f"Lỗi khi crawl {url} sau {max_retries} lần thử: {str(e)}")
                return {"url": url, "content": f"Lỗi: {str(e)}"}

async def crawl_multiple_urls(urls, max_concurrent=1):
    sem = Semaphore(max_concurrent)
    tasks = [crawl_product_info(url, sem) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # for result in results:
    #     record = {
    #         "text" : result.content,
    #         "embedding" : get_embedding(result.content)
    #     }
    #     produce('rag_embeddings', json.dumps(record).encode('utf-8'))
    with open(f"product_info.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Đã lưu kết quả vào product_info.json")
    return results

if __name__ == "__main__":
    url = ["https://tiki.vn/sach-combo-khong-tu-tinh-hoa-khong-tu-tam-dac-p277209976.html"]
    asyncio.run(crawl_multiple_urls(url))