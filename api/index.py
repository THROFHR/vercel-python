import urllib.parse
from http.server import BaseHTTPRequestHandler

import requests
import yaml


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            url = urllib.parse.urlparse(self.path)
            sub_path = urllib.parse.unquote(url.path.split('/sub/')[1])

            # 下载文件
            def download_file(url):
                response = requests.get(url)
                response.raise_for_status()
                return yaml.safe_load(response.text)

            # 删除包含特定关键词的节点
            def remove_nodes(data, keyword):
                if 'proxies' in data:
                    data['proxies'] = [proxy for proxy in data['proxies'] if keyword not in proxy]
                return data

            # 插入内容到指定位置
            def insert_content(data, content, key):
                if key in data:
                    data[key] = content + data[key]
                return data

            # 获取文件
            sub_data = download_file(sub_path)
            listeners_data = download_file('https://gist.githubusercontent.com/linsk/10e8cc30145a5a5fd126d2a0296e9373/raw/02bb74ebaeef623f747784ef94be5af865316c61/listeners.yml')
            proxies_data = download_file('https://gist.githubusercontent.com/linsk/d89554a40ae9a55c3c9f2c1e39fab72b/raw/71b488f2141116c85fefbbc22db23f82b8bfa667/proxies.yml')

            # 处理文件
            data = remove_nodes(sub_data, '订阅')
            data = insert_content(data, listeners_data['listeners'], 'external-controller')
            data = insert_content(data, proxies_data['proxies'], 'proxies')

            # 返回处理后的文件
            response_data = yaml.safe_dump(data)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(response_data.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
        return