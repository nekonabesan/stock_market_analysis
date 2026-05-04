import argparse
import shutil
import subprocess
import tempfile
import requests
import re
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

class PDFUrlToMarkdown:
    def __init__(self):
        pass

    def pdf_url_to_markdown(
        self,
        pdf_url: str, 
        directory_path: str, 
        markitdown_cmd: str = "markitdown", 
        timeout: int = 30
    ) -> str:
        # markitdown が見つかるか確認（無ければ pdftotext フォールバックを行う）
        markitdown_available = shutil.which(markitdown_cmd) is not None

        # PDF をダウンロードして一時ファイルへ保存
        resp = requests.get(pdf_url, stream=True, timeout=timeout)
        resp.raise_for_status()

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tf:
                tmp_path = tf.name
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        tf.write(chunk)
            # PDFファイル名を取得
            file_name = Path(urlparse(pdf_url).path).name
            # まず MarkItDown を呼び出して Markdown に変換（存在すれば）
            out_path = Path(directory_path) / f"{file_name}.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            if markitdown_available:
                proc = subprocess.run(
                    [markitdown_cmd, tmp_path, "-o", str(out_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                # プロセスがシグナルで終了（負の rc）や非ゼロ終了ならフォールバックへ
                if proc.returncode == 0:
                    print(f"Generated: {out_path.resolve()}")
                    return str(out_path.resolve())
                else:
                    stderr = proc.stderr.strip()
                    print(f"markitdown failed (rc={proc.returncode}). Falling back to pdftotext if available. stderr:\n{stderr}")

            # フォールバック: pdftotext (poppler-utils) を使ってテキスト抽出し簡易 Markdown を生成
            pdftotext_cmd = shutil.which("pdftotext")
            if pdftotext_cmd is None:
                # 失敗: markitdown が無いか失敗し、pdftotext も無い
                raise RuntimeError("PDF conversion failed: no working markitdown and pdftotext not found.")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tf_txt:
                txt_path = tf_txt.name

            try:
                p2 = subprocess.run([pdftotext_cmd, "-layout", tmp_path, txt_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if p2.returncode != 0:
                    raise RuntimeError(f"pdftotext failed (rc={p2.returncode}):\n{p2.stderr}")

                # 読み込んで簡易 Markdown に変換（段落ごとに空行を入れる）
                with open(txt_path, "r", encoding="utf-8", errors="ignore") as fh:
                    txt = fh.read()

                # 連続空行を2つの改行にして段落化
                paragraphs = [p.strip() for p in re.split(r"\n{2,}", txt) if p.strip()]
                md_lines = []
                for p in paragraphs:
                    # 行内の改行はスペースに置換して段落を一行にまとめる
                    single = " ".join([ln.strip() for ln in p.splitlines() if ln.strip()])
                    md_lines.append(single)

                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write("\n\n".join(md_lines))

                print(f"Generated (pdftotext fallback): {out_path.resolve()}")
                return str(out_path.resolve())
            finally:
                if os.path.exists(txt_path):
                    try:
                        os.remove(txt_path)
                    except Exception:
                        pass
        finally:
            # 一時ファイルは必ず削除
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
        
