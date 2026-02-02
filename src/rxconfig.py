"""Reflex application configuration."""

import os

import reflex as rx

config = rx.Config(
    app_name="alberto_codes_site",
    api_url=os.environ.get("API_URL", "http://localhost:8000"),
    deploy_url=os.environ.get("DEPLOY_URL", "http://localhost:3000"),
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
