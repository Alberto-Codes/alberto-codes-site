"""Reflex application configuration."""

import reflex as rx

config = rx.Config(
    app_name="alberto_codes_site",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
