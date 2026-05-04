import logging
import requests
from readability import Document
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from pathlib import Path

logger = logging.getLogger(__name__)

class WebpageToMarkdown:

    def __init__(self):
        pass

    def webpage_to_markdown(
        self,
        url: str,
        directory_path: str | Path,
        timeout: int = 10,
        user_agent: str | None = None
    ) -> Path:
        """
        指定したURLのWebページをMarkdown形式で保存する関数
        Args:
            url (str): WebページのURL
            directory_path (str): Markdownファイルを保存するディレクトリのパス
            timeout (int, optional): HTTPリクエストのタイムアウト時間（秒）。デフォルトは10秒。
            user_agent (str, optional): HTTPリクエストのUser-Agentヘッダー。デフォルトはNone（"Mozilla/5.0 (compatible)"が使用される）。
        Returns:
            str: 生成されたMarkdownファイルのパス
        """
        markdown = self.get_markdown_from_url(url, timeout, user_agent)
        # Markdownファイル名を取得
        file_name = Path(urlparse(url).path).name
        # 生成された Markdown をファイルに出力
        out_path = Path(directory_path) / f"{file_name}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        return out_path.resolve()
    
    def get_markdown_from_url(
        self,
        url: str,
        timeout: int = 10,
        user_agent: str | None = None
    ) -> str:
        headers = {"User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        html = resp.text

        # Try Readability to extract main content
        try:
            doc = Document(html)
            cleaned_html = doc.summary()
            title = (doc.short_title() or doc.title() or "").strip()
        except Exception as e:
            logger.warning("Readability failed for %s: %s", url, e)
            cleaned_html = html
            title = ""

        # Normalize links/images to absolute URLs and remove unwanted tags
        soup = BeautifulSoup(cleaned_html, "html.parser")
        for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav", "aside", "form", "advertisement", "ins"]):
            tag.decompose()

        # Make img/src and a/href absolute
        for img in soup.find_all("img"):
            if img.get("src"):
                img["src"] = urljoin(url, img["src"])
        for a in soup.find_all("a"):
            if a.get("href"):
                a["href"] = urljoin(url, a["href"])

        cleaned_html = str(soup)

        # Convert to Markdown
        md_text = (f"# {title}\n\n" if title else "")
        md_text += md(cleaned_html, heading_style="ATX")

        return md_text