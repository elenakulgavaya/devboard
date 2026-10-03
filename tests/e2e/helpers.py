import uuid
from playwright.sync_api import Page, expect


def uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def create_task(page: Page, title: str, **kwargs) -> None:
    page.locator("button", has_text="+ New Task").click()
    page.locator("#task-title").fill(title)
    if desc := kwargs.get("description"):
        page.locator("#task-desc").fill(desc)
    if labels := kwargs.get("labels"):
        page.locator("#task-labels").fill(labels)
    if status := kwargs.get("status"):
        page.locator("#task-status").select_option(status)
    if priority := kwargs.get("priority"):
        page.locator("#task-priority").select_option(priority)
    if assignee := kwargs.get("assignee"):
        page.locator("#task-assignee").fill(assignee)
    if wiki_page := kwargs.get("wiki_page"):
        page.locator("#task-wiki-page").select_option(label=wiki_page)
    page.locator("#task-form button", has_text="Save").click()
    expect(page.locator("#tasks-list")).to_contain_text(title)


def delete_task(page: Page, title: str) -> None:
    card = page.locator("#tasks-list .card", has_text=title).first
    card.locator("button[title='Delete']").click()
    expect(page.locator("#tasks-list")).not_to_contain_text(title)


def create_wiki_page(page: Page, title: str, content: str = "") -> None:
    page.locator("button", has_text="+ New Page").click()
    page.locator("#page-title").fill(title)
    if content:
        page.locator("#page-content").fill(content)
    page.locator("#page-form button", has_text="Save").click()
    expect(page.locator("#pages-list")).to_contain_text(title)


def delete_wiki_page(page: Page, title: str) -> None:
    card = page.locator("#pages-list .card", has_text=title).first
    card.locator("button[title='Delete']").click()
    expect(page.locator("#pages-list")).not_to_contain_text(title)
