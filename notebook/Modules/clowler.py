import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

class Clowler:
    def __init__(self):
        pass

    def _crawl(
        self,
        url: str,
        depth: int,
        max_depth: int,
        visited: set,
        results: list,
        domain: str,
        keyword: str,
        return_dom: bool = False,
    ) -> None:
            if depth > max_depth:
                return
            if url in visited:
                return

            visited.add(url)

            try:
                res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                res.raise_for_status()
            except Exception:
                return

            soup = BeautifulSoup(res.text, "html.parser")
            text = soup.get_text(separator="\n")

            # キーワード一致行を抽出
            matched_lines = []
            for line in text.split("\n"):
                if keyword.lower() in line.lower():
                    matched_lines.append(line.strip())

            if matched_lines:
                if return_dom:
                    results.append({"url": url, "soup": soup, "matches": matched_lines})
                else:
                    for line in matched_lines:
                        results.append((url, line))

            # 子リンクを探索
            for a in soup.find_all("a", href=True):
                child = urljoin(url, a["href"])
                child, _ = urldefrag(child)
                parsed = urlparse(child)

                # 同一ドメインのみクロール
                if parsed.netloc == domain:
                    self._crawl(child, depth + 1, max_depth, visited, results, domain, keyword, return_dom)



    # 使用例
    #rl = "https://www.example.com/ir"
    #keyword = "決算"
    #matches = crawl_domain(url, keyword)

    #for url, line in matches:
    #    print(url, ":", line)
    def crawl_domain(
        self,
        start_url: str,
        keyword: str,
        max_depth: int = 3,
        return_dom: bool = False,
    ) -> list:
        visited = set()
        results = []

        domain = urlparse(start_url).netloc

        self._crawl(start_url, 0, max_depth, visited, results, domain, keyword, return_dom)
        return results


