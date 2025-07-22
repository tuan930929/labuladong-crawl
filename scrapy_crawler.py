import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import os

class LabuladongSpider(CrawlSpider):
    name = 'labuladong'
    allowed_domains = ['labuladong.online']
    start_urls = ['https://labuladong.online/']
    
    rules = (
        # Trích xuất liên kết từ trang và theo dõi chúng
        Rule(LinkExtractor(allow=r'.*labuladong\.online.*'), callback='parse_item', follow=True),
    )
    
    def __init__(self, *args, **kwargs):
        super(LabuladongSpider, self).__init__(*args, **kwargs)
        self.output_dir = 'output_html'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def parse_item(self, response):
        # Tạo tên file từ URL
        filename = response.url.replace('https://labuladong.online/', '').replace('/', '_')
        if not filename:
            filename = "index"
        filepath = os.path.join(self.output_dir, f"{filename}.html")
        
        # Sửa đổi các liên kết trong HTML để trỏ đến các file HTML cục bộ
        body = response.body.decode('utf-8')
        
        # Lưu toàn bộ nội dung HTML vào file
        with open(filepath, 'w', encoding='utf-8') as f:
            # Thêm base tag để đảm bảo các đường dẫn tương đối hoạt động đúng
            base_tag = f'<base href="https://labuladong.online/">'
            # Chèn base tag vào phần head của HTML
            if '<head>' in body:
                body = body.replace('<head>', f'<head>{base_tag}')
            else:
                body = f'<html><head>{base_tag}</head>{body}</html>'
            
            f.write(body)
        
        self.logger.info(f"Đã lưu: {response.url} -> {filepath}")
        
        return {
            'url': response.url,
            'file': filepath
        }

# Chạy crawler
if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False,  # Tuân thủ robots.txt
        'DOWNLOAD_DELAY': 1,     # Tạm dừng 1 giây giữa các request
    })
    
    process.crawl(LabuladongSpider)
    process.start()