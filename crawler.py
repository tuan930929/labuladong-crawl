import requests
from bs4 import BeautifulSoup
import os
import time

class LabuladongCrawler:
    def __init__(self, base_url="https://labuladong.online/", output_dir="output_html"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls = set()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Tạo thư mục output nếu chưa tồn tại
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def get_page_content(self, url):
        """Tải nội dung của một trang web"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải trang {url}: {e}")
            return None
    
    def parse_page(self, html_content, url):
        """Phân tích cú pháp HTML và trích xuất nội dung"""
        if not html_content:
            return None
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Trích xuất các liên kết và sửa đổi chúng để trỏ đến các file HTML cục bộ
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Chuyển đổi URL tương đối thành URL tuyệt đối
            if href.startswith('/'):
                href = self.base_url.rstrip('/') + href
            elif not href.startswith(('http://', 'https://')):
                href = self.base_url.rstrip('/') + '/' + href
            
            # Chỉ xử lý các liên kết từ cùng domain
            if href.startswith(self.base_url):
                # Tạo tên file HTML từ URL
                local_filename = href.replace(self.base_url, "").replace("/", "_")
                if not local_filename:
                    local_filename = "index"
                local_filename = f"{local_filename}.html"
                
                # Cập nhật href để trỏ đến file HTML cục bộ
                a_tag['href'] = local_filename
        
        # Trích xuất các liên kết để tiếp tục crawl
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Chỉ lấy các liên kết từ cùng domain và chưa được truy cập
            original_href = href
            if href.endswith('.html'):
                # Chuyển đổi ngược lại để lấy URL gốc
                original_href = self.base_url + href.replace('.html', '').replace('_', '/')
            
            if original_href.startswith(self.base_url) and original_href not in self.visited_urls:
                links.append(original_href)
        
        # Sửa đổi các đường dẫn CSS và JS để sử dụng CDN hoặc đường dẫn tương đối
        for tag in soup.find_all(['link', 'script'], src=True):
            if tag['src'].startswith('/'):
                tag['src'] = self.base_url.rstrip('/') + tag['src']
        
        for tag in soup.find_all(['link'], href=True):
            if tag['href'].startswith('/'):
                tag['href'] = self.base_url.rstrip('/') + tag['href']
        
        # Thêm base tag để đảm bảo các đường dẫn tương đối hoạt động đúng
        base_tag = soup.new_tag('base')
        base_tag['href'] = self.base_url
        if soup.head:
            soup.head.insert(0, base_tag)
        
        return {
            "url": url,
            "html": str(soup),
            "links": links
        }
    
    def save_page(self, page_data):
        """Lưu nội dung trang vào file HTML"""
        if not page_data:
            return
        
        # Tạo tên file từ URL
        filename = page_data["url"].replace(self.base_url, "").replace("/", "_")
        if not filename:
            filename = "index"
        filename = os.path.join(self.output_dir, f"{filename}.html")
        
        # Lưu dữ liệu vào file HTML
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_data["html"])
        
        print(f"Đã lưu: {page_data['url']} -> {filename}")
    
    def crawl(self, start_url=None, max_pages=100):
        """Bắt đầu crawl từ URL ban đầu"""
        if start_url is None:
            start_url = self.base_url
        
        urls_to_visit = [start_url]
        page_count = 0
        
        while urls_to_visit and page_count < max_pages:
            current_url = urls_to_visit.pop(0)
            
            # Kiểm tra xem URL đã được truy cập chưa
            if current_url in self.visited_urls:
                continue
            
            print(f"Đang crawl: {current_url}")
            self.visited_urls.add(current_url)
            
            # Tải và phân tích trang
            html_content = self.get_page_content(current_url)
            page_data = self.parse_page(html_content, current_url)
            
            if page_data:
                self.save_page(page_data)
                urls_to_visit.extend(page_data["links"])
            
            page_count += 1
            
            # Tạm dừng để tránh gửi quá nhiều request
            time.sleep(1)
        
        print(f"Đã hoàn thành crawl {page_count} trang.")

# Chạy crawler
if __name__ == "__main__":
    crawler = LabuladongCrawler()
    crawler.crawl(max_pages=50)  # Giới hạn số trang để crawl