"""
Cross-service tests: task ↔ wiki integration.
"""
import pytest
from playwright.sync_api import Page, expect
from helpers import uid, create_task, delete_task, create_wiki_page, delete_wiki_page


def go_to_wiki(page: Page) -> None:
    page.locator("#nav-wiki").click()
    expect(page.locator("#section-wiki")).to_be_visible()


def go_to_tasks(page: Page) -> None:
    page.locator("#nav-tasks").click()
    expect(page.locator("#section-tasks")).to_be_visible()


def test_task_shows_wiki_badge_when_linked(logged_in_page: Page):
    p = logged_in_page
    page_title = uid("Linked Page ")
    task_title = uid("Linked Task ")
    try:
        # Create wiki page first so it appears in the task form's dropdown
        go_to_wiki(p)
        create_wiki_page(p, page_title)

        # Create task linked to that wiki page
        go_to_tasks(p)
        create_task(p, task_title, wiki_page=page_title)

        card = p.locator("#tasks-list .card", has_text=task_title)
        expect(card.locator(".badge-wiki")).to_be_visible()
        expect(card.locator(".badge-wiki")).to_contain_text(page_title)
    finally:
        delete_task(p, task_title)
        go_to_wiki(p)
        delete_wiki_page(p, page_title)


def test_clicking_wiki_badge_navigates_to_wiki_section(logged_in_page: Page):
    p = logged_in_page
    page_title = uid("Nav Page ")
    task_title = uid("Nav Task ")
    try:
        go_to_wiki(p)
        create_wiki_page(p, page_title)

        go_to_tasks(p)
        create_task(p, task_title, wiki_page=page_title)

        card = p.locator("#tasks-list .card", has_text=task_title)
        card.locator(".badge-wiki").click()

        # Should have navigated to the wiki section
        expect(p.locator("#section-wiki")).to_be_visible()
        expect(p.locator("#section-tasks")).to_be_hidden()
        # The linked page should be visible
        expect(p.locator("#pages-list")).to_contain_text(page_title)
    finally:
        go_to_tasks(p)
        delete_task(p, task_title)
        go_to_wiki(p)
        delete_wiki_page(p, page_title)


def test_wiki_page_dropdown_includes_existing_pages(logged_in_page: Page):
    p = logged_in_page
    page_title = uid("Dropdown Page ")
    try:
        go_to_wiki(p)
        create_wiki_page(p, page_title)

        go_to_tasks(p)
        p.locator("button", has_text="+ New Task").click()
        options = p.locator("#task-wiki-page option")
        option_texts = [options.nth(i).inner_text() for i in range(options.count())]
        assert page_title in option_texts
        p.locator("#task-form button", has_text="Cancel").click()
    finally:
        go_to_wiki(p)
        delete_wiki_page(p, page_title)


def test_unlink_wiki_page_from_task(logged_in_page: Page):
    p = logged_in_page
    page_title = uid("Unlink Page ")
    task_title = uid("Unlink Task ")
    try:
        go_to_wiki(p)
        create_wiki_page(p, page_title)

        go_to_tasks(p)
        create_task(p, task_title, wiki_page=page_title)

        # Edit task to remove wiki link
        card = p.locator("#tasks-list .card", has_text=task_title)
        card.locator("button[title='Edit']").click()
        p.locator("[id^='et-wiki-']").select_option("")  # "No wiki page"
        p.locator(".card", has_text="Editing task #").locator("button", has_text="Save").click()

        card = p.locator("#tasks-list .card", has_text=task_title)
        expect(card.locator(".badge-wiki")).not_to_be_visible()
    finally:
        delete_task(p, task_title)
        go_to_wiki(p)
        delete_wiki_page(p, page_title)
