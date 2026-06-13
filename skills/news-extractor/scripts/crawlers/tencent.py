# -*- coding: utf-8 -*-
"""
腾讯新闻爬虫
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List, Optional

from parsel import Selector
from pydantic import Field

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parents[1]))

from models import ContentItem, ContentType, NewsItem, NewsMetaInfo, RequestHeaders as BaseRequestHeaders
from crawlers.base import BaseNewsCrawler
from crawlers.fetchers import CurlCffiFetcher, FetchRequest


FIXED_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
FIXED_COOKIE = ''


class RequestHeaders(BaseRequestHeaders):
    user_agent: str = Field(default=FIXED_USER_AGENT, alias="User-Agent")
    cookie: str = Field(default=FIXED_COOKIE, alias="Cookie")


class TencentNewsCrawler(BaseNewsCrawler):
    fetch_strategy = CurlCffiFetcher

    def __init__(
        self,
        new_url: str,
        save_path: str = "data/",
        headers: Optional[RequestHeaders] = None,
        fetcher: Optional[CurlCffiFetcher] = None,
    ):
        super().__init__(new_url, save_path, headers=headers, fetcher=fetcher)

    @property
    def get_base_url(self) -> str:
        return "https://news.qq.com"

    def get_article_id(self) -> str:
        try:
            news_id = self.new_url.split("/a/")[1].split("?")[0].strip("/")
            return news_id
        except Exception as exc:
            raise ValueError(f"解析文章ID失败，请检查URL是否正确: {exc}") from exc

    def build_fetch_request(self) -> FetchRequest:
        request = super().build_fetch_request()
        request.impersonate = "chrome"
        return request

    def _extract_window_data(self, html_content: str) -> dict:
        try:
            pattern = r'window\.DATA\s*=\s*(\{[\s\S]*?\});'
            match = re.search(pattern, html_content)

            if match:
                data_json = match.group(1)
                return json.loads(data_json)
        except (json.JSONDecodeError, AttributeError) as e:
            self.logger.warning(f"Failed to extract window.DATA: {e}")

        return {}

    def parse_html_to_news_meta(self, html_content: str) -> NewsMetaInfo:
        self.logger.info("Start to parse html to news meta, news_url: %s", self.new_url)

        window_data = self._extract_window_data(html_content)

        # 处理问答类型的页面
        entity_type = window_data.get("entity_type", "")
        if entity_type == "question":
            # 问答页面
            card = window_data.get("card", {})
            author_name = card.get("chlname", "")
            publish_time = window_data.get("time", "")
        else:
            # 普通新闻页面
            author_name = window_data.get("media", "")
            publish_time = window_data.get("pubtime", "")

        return NewsMetaInfo(
            publish_time=publish_time.strip(),
            author_name=author_name.strip(),
            author_url="",
        )

    def parse_html_to_news_content(self, html_content: str) -> List[ContentItem]:
        contents = []

        # 首先尝试从window.DATA提取内容
        window_data = self._extract_window_data(html_content)

        # 检查是否是问答类型页面
        entity_type = window_data.get("entity_type", "")
        if entity_type == "question":
            # 问答页面 - 提取问题描述和相关文章
            desc = window_data.get("desc", "")
            if desc:
                contents.append(ContentItem(type=ContentType.TEXT, content=desc, desc=desc))

            # 添加相关文章信息
            relate_info = window_data.get("relate_extend_infos", {})
            if relate_info:
                relate_title = relate_info.get("longTitle", relate_info.get("title", ""))
                relate_abstract = relate_info.get("abstract", "")
                relate_url = relate_info.get("url", "")

                if relate_title:
                    contents.append(ContentItem(type=ContentType.TEXT, content=f"\n\n相关文章：{relate_title}", desc=relate_title))
                if relate_abstract:
                    contents.append(ContentItem(type=ContentType.TEXT, content=relate_abstract, desc=relate_abstract))
                if relate_url:
                    contents.append(ContentItem(type=ContentType.TEXT, content=f"\n原文链接：{relate_url}", desc=relate_url))

            # 添加图片（如果有）
            thumbnails = window_data.get("thumbnails_qqnews", [])
            for img_url in thumbnails:
                if img_url:
                    contents.append(ContentItem(type=ContentType.IMAGE, content=img_url, desc=img_url))

            return contents

        # 普通新闻页面 - 使用原有的解析逻辑
        selector = Selector(text=html_content)
        elements = selector.xpath('//div[@class="rich_media_content"]/*')
        for element in elements:
            if element.root.tag == 'p':
                has_img = element.xpath('.//img').get() is not None

                if has_img:
                    img_url = element.xpath('.//img/@src').get('')
                    if img_url:
                        contents.append(ContentItem(type=ContentType.IMAGE, content=img_url, desc=img_url))
                else:
                    text = element.xpath('string()').get('').strip()
                    if text:
                        contents.append(ContentItem(type=ContentType.TEXT, content=text, desc=text))

            elif element.root.tag == 'img':
                img_url = element.xpath('./@src').get('')
                if img_url:
                    contents.append(ContentItem(type=ContentType.IMAGE, content=img_url, desc=img_url))

            elif element.root.tag == 'video':
                video_url = element.xpath('./@src').get('')
                if video_url:
                    contents.append(ContentItem(type=ContentType.VIDEO, content=video_url, desc=video_url))

        return contents

    def parse_content(self, html: str) -> NewsItem:
        selector = Selector(text=html)

        # 尝试从h1标签获取标题，如果没有则从title标签获取
        title = selector.xpath('//h1/text()').get("")
        if not title:
            title = selector.xpath('//title/text()').get("")
            # 移除" _腾讯新闻"等后缀
            if title:
                title = title.split('_')[0].strip()

        if not title:
            raise ValueError("Failed to get title")

        meta_info = self.parse_html_to_news_meta(html)
        contents = self.parse_html_to_news_content(html)

        return self.compose_news_item(
            title=title.strip(),
            meta_info=meta_info,
            contents=contents,
        )
