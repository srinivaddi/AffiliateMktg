import json
import time
import asyncio
from datetime import datetime, timedelta, timezone

import iso8601
from bs4 import BeautifulSoup

from affiliate_mktg.src.blog.blog_generator import BlogGenerator
from affiliate_mktg.src.blog.blog_service import BlogService
from affiliate_mktg.src.utils.common import (
    get_current_year_month,
    to_camel_case,
    get_elasped_time,
    is_similar_string,
)
from affiliate_mktg.src.config.loader import get_blog_config
from affiliate_mktg.src.core.enums import Models
from typing import Optional
from affiliate_mktg.src.core.models import BlogInputConfig
from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
configValues = get_blog_config()


class BlogManager:
    def __init__(self):
        logger.info("Hello from BlogManager!")
        self.blogService = BlogService()
        self.blogGenerator = BlogGenerator()

        self.BLOG_ID = configValues["BLOG_ID"]
        self.BASE_URL = configValues["BASE_URL"]
        self.LABELS = configValues["LABELS"]
        self.LOCATION_JSON = configValues["LOCATION_JSON"]
        self.LOCATION = json.loads(self.LOCATION_JSON)
        self.LIVE_POST = configValues["LIVE_POST"]
        self.FILE_EXTENSION = configValues["FILE_EXTENSION"]
        self.MODEL_NAME = configValues["MODEL_NAME"]
        self.MODEL_OPTIONS_JSON = configValues["MODEL_OPTIONS_JSON"]
        self.MODEL_OPTIONS = json.loads(self.MODEL_OPTIONS_JSON)
        self.TOPIC = configValues["TOPIC"]
        self.BOOL_MAP = {
            "True": True,
            "False": False,
            "true": True,
            "false": False,
        }
        self.STREAM = self.BOOL_MAP.get(configValues["STREAM"], False)
        self.TOPIC_URL = to_camel_case(self.TOPIC).lower().replace(" ", "-")
        self.SYSTEM_PROMPT_ROLE = configValues["SYSTEM_PROMPT_ROLE"]
        self.SYSTEM_PROMPT_STYLE = configValues["SYSTEM_PROMPT_STYLE"]
        self.SYSTEM_PROMPT_TEMPLATE = configValues["SYSTEM_PROMPT_TEMPLATE"]
        self.SYSTEM_PROMPT = self.SYSTEM_PROMPT_TEMPLATE.format(
            SYSTEM_PROMPT_ROLE=self.SYSTEM_PROMPT_ROLE,
            SYSTEM_PROMPT_STYLE=self.SYSTEM_PROMPT_STYLE,
        )
        self.USER_PROMPT_TEMPLATE = configValues["USER_PROMPT_TEMPLATE"]
        self.USER_PROMPT = self.USER_PROMPT_TEMPLATE.format(
            TOPIC=self.TOPIC, SYSTEM_PROMPT_STYLE=self.SYSTEM_PROMPT_STYLE
        )
        self.FILTER_POST_COUNT = configValues["FILTER_POST_COUNT"]
        self.FILTER_POST = configValues["FILTER_POST"]
        self.FILTER_DAYS = configValues["FILTER_DAYS"]

    def _initialize_service(self):
        try:
            return self.blogService.get_blogger_service()
        except ImportError as e:
            logger.error(f"Error initializing BlogService: {e}", exc_info=True)
            return None

    async def get_blog_all_posts(self, days):
        try:
            service = self._initialize_service()

            user_info = service.users().get(userId="self").execute()
            logger.info(f"User Display Name: {user_info['displayName']}")

            utc_now = datetime.now(timezone.utc)
            x_days_ago = utc_now - timedelta(days=int(days) + 1)

            request = service.posts().list(
                blogId=self.BLOG_ID,
                maxResults=self.FILTER_POST_COUNT,
                fetchBodies=False,
            )
            all_recent_posts = []
            while request is not None:
                response = request.execute()
                for post in response.get("items", []):
                    published_date = iso8601.parse_date(post["published"])
                    if published_date >= x_days_ago:
                        all_recent_posts.append(post)
                request = service.posts().list_next(request, response)

            for post in all_recent_posts:
                logger.info(f"Title: {post['title']}")
                logger.info(f"Published: {post['published']}")
                logger.info(f"URL: {post['url']}")
                logger.info("-" * 40)

            return all_recent_posts

        except Exception as e:
            logger.error(
                f"An error occurred while getting blog posts: {e}",
                exc_info=True,
            )

    async def _post_blog(
        self,
        blog_post: str,
        topic: str,
        blog_url: str,
        labels: str,
        location: str,
        live_post: str,
    ):
        try:
            if not blog_post:
                logger.info("Blog post content is empty. Cannot publish.")
                return

            logger.info("Blog post content is not empty. Publishing...")

            service = self._initialize_service()

            post_body = {
                "title": topic,
                "content": blog_post,
                "labels": labels,
                "location": location,
                "url": blog_url,
                "status": "LIVE" if live_post is True else "DRAFT",
            }

            post = (
                service.posts()
                .insert(blogId=self.BLOG_ID, body=post_body)
                .execute()
            )
            logger.info(f"Post published: {post['url']}")
        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)

    async def _clean_blog_post(self, blog_post: str) -> str:
        try:
            doctype_marker = "<!DOCTYPE html>"
            html_start_marker = "<html>"
            html_end_marker = "</html>"

            start_index = blog_post.find(doctype_marker)
            doctype_missing = start_index == -1

            if doctype_missing:
                start_index = blog_post.find(html_start_marker)

            end_index = blog_post.find(html_end_marker)

            if start_index != -1 and end_index != -1:
                extracted_html = blog_post[
                    start_index : end_index + len(html_end_marker)
                ]

                if doctype_missing:
                    extracted_html = f"{doctype_marker}\n{extracted_html}"

                for char in ["\n", "\r", "\t", "\b", "\f", "\a", "•"]:
                    extracted_html = extracted_html.replace(char, " ")

                return extracted_html

            return blog_post

        except Exception as e:
            logger.error(
                f"An error occurred while cleaning the blog post: {e}",
                exc_info=True,
            )
            return blog_post

    async def _beautify_html_blog_post(
        self,
        blog_post: str,
        topic_args_post: str,
        topic_args_image: str,
    ) -> str:
        try:
            soup = BeautifulSoup(blog_post, "html.parser")

            img_tag = soup.find("img")
            if img_tag:
                img_tag["src"] = topic_args_image

            for anchor_id in ("#link", "link"):
                anchor_tag = soup.find("a", id=anchor_id)
                if anchor_tag:
                    anchor_tag["href"] = topic_args_post

            anchor_tag = soup.find("a")
            if anchor_tag:
                anchor_tag["href"] = topic_args_post

            logger.info(soup.prettify())
            return soup.prettify()

        except Exception as e:
            logger.error(
                f"An error occurred while cleaning the blog post: {e}",
                exc_info=True,
            )
            return blog_post

    def _is_valid_HTML_tag(self, blog_post: str) -> bool:
        try:
            BeautifulSoup(blog_post, "html.parser")
            return True
        except Exception:
            return False

    async def _generate_blog_post(
        self,
        system_prompt,
        user_prompt,
        model_name,
        model_options,
    ):
        return await self.blogGenerator.generate_blog_by_model(
            system_prompt, user_prompt, model_name, model_options
        )

    async def _generate_blog_post_stream(
        self,
        system_prompt,
        user_prompt,
        model_name,
        model_options,
    ):
        return await self.blogGenerator.generate_blog_by_model_stream(
            system_prompt, user_prompt, model_name, model_options
        )

    async def generate_blog(
        self,
        topic_args: str,
        topic_args_post: str,
        topic_args_image: str,
        systempromptrole_args: str,
        systempromptstyle_args: str,
    ) -> str:
        try:
            model_options = self.MODEL_OPTIONS
            stream = self.STREAM

            model_name = self.MODEL_NAME
            if model_name == "":
                model_name = Models.default()

            system_prompt = self.SYSTEM_PROMPT
            if systempromptrole_args and systempromptstyle_args:
                system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
                    SYSTEM_PROMPT_ROLE=systempromptrole_args,
                    SYSTEM_PROMPT_STYLE=systempromptstyle_args,
                )

            user_prompt = self.USER_PROMPT
            if topic_args:
                user_prompt = self.USER_PROMPT_TEMPLATE.format(
                    TOPIC=topic_args,
                    SYSTEM_PROMPT_STYLE=systempromptrole_args,
                )

            start_time = time.perf_counter()

            if not stream:
                blog_post = await self._generate_blog_post(
                    system_prompt, user_prompt, model_name, model_options
                )
            else:
                blog_post = await self._generate_blog_post_stream(
                    system_prompt, user_prompt, model_name, model_options
                )

            elapsed_time = get_elasped_time(start_time, time.perf_counter())
            logger.info(
                f"The method generate_blog took {elapsed_time:.4f} seconds to run."
            )

            logger.info(blog_post)

            blog_post = await self._beautify_html_blog_post(
                blog_post, topic_args_post, topic_args_image
            )
            blog_post = await self._clean_blog_post(blog_post)

            logger.info(blog_post)

            return blog_post

        except Exception as e:
            logger.error(
                f"An error occurred while generating blog: {e}",
                exc_info=True,
            )
            return ""

    async def post_blog_blogger(
        self,
        blog_post: str,
        topic_args: str,
        topicurl_arg: str,
        labels_args: str,
    ):
        try:
            model_name = self.MODEL_NAME
            if model_name == "":
                model_name = Models.default()

            topic = self.TOPIC
            if topic_args:
                topic = topic_args

            topic_url = self.TOPIC_URL
            if topicurl_arg != "":
                topic_url = topicurl_arg

            if blog_post and len(blog_post) > 0:
                year, month = get_current_year_month()
                blog_url = (
                    f"{self.BASE_URL}{year}/{month}/{topic_url}.{self.FILE_EXTENSION}"
                )
                location = self.LOCATION
                live_post = self.LIVE_POST

                labels = self.LABELS
                if labels_args:
                    labels = labels_args

                await self._post_blog(
                    blog_post, topic, blog_url, labels, location, live_post
                )
                logger.info("Blog posting completed successfully.")
            else:
                logger.info("Blog post generation failed.")

        except Exception as e:
            logger.error(
                f"An error occurred while posting blog to blogger: {e}",
                exc_info=True,
            )

    async def blog_post_exists(
        self, blogInputConfig: Optional[BlogInputConfig] = None
    ) -> bool:
        try:
            if blogInputConfig is None:
                return False
            existing_post = []
            if self.FILTER_POST:
                existing_post = await self.get_blog_all_posts(self.FILTER_DAYS)
                if existing_post:
                    post_exists = any(
                        is_similar_string(
                            blogInputConfig.items_arg.short_display_value,
                            post["title"],
                            0.90,
                        )
                        for post in existing_post
                    )
                    return post_exists
                return False
            return False

        except Exception as e:
            logger.error(
                f"An error occurred while generating blog and posting: {e}",
                exc_info=True,
            )
            return False

    async def generate_blog_post_blogger(
        self, blogInputConfig: BlogInputConfig
    ):
        try:
            blog_exists = await self.blog_post_exists(blogInputConfig)
            if not blog_exists:
                logger.info(
                    f"Generating blog post for item: {blogInputConfig.items_arg.short_display_value}"
                )
                blog_post = await self.generate_blog(
                    topic_args=blogInputConfig.topic_arg,
                    topic_args_post=blogInputConfig.topic_arg_post,
                    topic_args_image=blogInputConfig.items_arg.images[0].url,
                    systempromptrole_args=blogInputConfig.systempromptstyle_arg,
                    systempromptstyle_args=blogInputConfig.systempromptstyle_arg,
                )

                if not self._is_valid_HTML_tag(blog_post):
                    logger.info(
                        "Generated blog post is not valid HTML. Cannot publish."
                    )
                    return

                logger.info(
                    f"Posting blog post for item: {blogInputConfig.items_arg.short_display_value}"
                )
                await self.post_blog_blogger(
                    blog_post=blog_post,
                    topic_args=blogInputConfig.topic_arg,
                    topicurl_arg=blogInputConfig.topicurl_arg,
                    labels_args=blogInputConfig.labels_arg,
                )

                return True, f"Generated and posted blog for {blogInputConfig.items_arg.short_display_value}"
            else:
                return (
                    False,
                    f"Blog with title '{blogInputConfig.items_arg.short_display_value}' has already been posted in last {self.FILTER_DAYS} day(s) and hence blog generate and post skipped for this blog",
                )

        except Exception as e:
            logger.error(
                f"An error occurred while generating blog and posting: {e}",
                exc_info=True,
            )
            return (
                False,
                f"An error occurred while generating blog and posting: {e}",
            )
