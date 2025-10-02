.PHONY: scrape api test format lint all

scrape:
	cd books_scraper && scrapy crawl books

api:
	uvicorn app.main:app --reload

test:
	pytest

format:
	black .
	ruff --fix .

lint:
	ruff .

all: scrape test api