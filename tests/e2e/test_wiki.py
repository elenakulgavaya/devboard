import pytest
from playwright.sync_api import Page, expect
from helpers import uid, create_wiki_page, delete_wiki_page


def go_to_wiki(page: Page) -> None:
    page.locator("#nav-wiki").click()
    expect(page.locator("#section-wiki")).to_be_visible()


# ── Navigation ────────────────────────────────────────────

def test_wiki_section_accessible_from_nav(logged_in_page: Page):
    go_to_wiki(logged_in_page)
    expect(logged_in_page.locator("#section-tasks")).to_be_hidden()


def test_tasks_section_accessible_from_nav(logged_in_page: Page):
    go_to_wiki(logged_in_page)
    logged_in_page.locator("#nav-tasks").click()
    expect(logged_in_page.locator("#section-tasks")).to_be_visible()
    expect(logged_in_page.locator("#section-wiki")).to_be_hidden()


# ── Form open / close ─────────────────────────────────────

def test_new_page_button_opens_form(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    expect(p.locator("#page-form")).to_be_hidden()
    p.locator("button", has_text="+ New Page").click()
    expect(p.locator("#page-form")).to_be_visible()


def test_cancel_button_closes_page_form(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    p.locator("button", has_text="+ New Page").click()
    p.locator("#page-form button", has_text="Cancel").click()
    expect(p.locator("#page-form")).to_be_hidden()


# ── Validation ────────────────────────────────────────────

def test_create_page_requires_title(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    p.locator("button", has_text="+ New Page").click()
    p.locator("#page-form button", has_text="Save").click()
    expect(p.locator("#page-title-err")).to_be_visible()
    expect(p.locator("#page-title-err")).to_contain_text("required")
    expect(p.locator("#page-form")).to_be_visible()


# ── CRUD ──────────────────────────────────────────────────

def test_create_minimal_wiki_page(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("Page ")
    try:
        create_wiki_page(p, title)
        expect(p.locator("#page-form")).to_be_hidden()
        expect(p.locator("#pages-list")).to_contain_text(title)
    finally:
        delete_wiki_page(p, title)


def test_create_page_with_content(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("Content Page ")
    try:
        create_wiki_page(p, title, content="## Hello\n\nSome **bold** text.")
        card = p.locator("#pages-list .card", has_text=title)
        expect(card).to_be_visible()
        expect(card).to_contain_text("## Hello")  # preview shows raw markdown
    finally:
        delete_wiki_page(p, title)


def test_edit_wiki_page(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    original = uid("Orig Page ")
    updated  = uid("Updated Page ")
    try:
        create_wiki_page(p, original)
        card = p.locator("#pages-list .card", has_text=original)
        card.locator("button[title='Edit']").click()
        p.locator("[id^='ep-title-']").fill(updated)
        p.locator(".card", has_text="Editing page #").locator("button", has_text="Save").click()
        expect(p.locator("#pages-list")).to_contain_text(updated)
        expect(p.locator("#pages-list")).not_to_contain_text(original)
    finally:
        delete_wiki_page(p, updated)


def test_edit_page_cancel_restores_original(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("Stable Page ")
    try:
        create_wiki_page(p, title)
        card = p.locator("#pages-list .card", has_text=title)
        card.locator("button[title='Edit']").click()
        p.locator("[id^='ep-title-']").fill("Should not appear")
        p.locator(".card", has_text="Editing page #").locator("button", has_text="Cancel").click()
        expect(p.locator("#pages-list")).to_contain_text(title)
        expect(p.locator("#pages-list")).not_to_contain_text("Should not appear")
    finally:
        delete_wiki_page(p, title)


def test_delete_wiki_page(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("Delete Page ")
    create_wiki_page(p, title)
    delete_wiki_page(p, title)
    expect(p.locator("#pages-list")).not_to_contain_text(title)


# ── Expand / collapse ─────────────────────────────────────

def test_clicking_page_card_expands_content(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("Expand Page ")
    try:
        create_wiki_page(p, title, content="Expandable content here")
        card = p.locator("#pages-list .card", has_text=title)
        page_id = card.get_attribute("id").split("-")[-1]
        expect(p.locator(f"#page-full-{page_id}")).to_be_hidden()
        card.locator(".card-hover").click()
        expect(p.locator(f"#page-full-{page_id}")).to_be_visible()
    finally:
        delete_wiki_page(p, title)


def test_clicking_expanded_page_collapses_it(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("Collapse Page ")
    try:
        create_wiki_page(p, title, content="Toggle me")
        card = p.locator("#pages-list .card", has_text=title)
        page_id = card.get_attribute("id").split("-")[-1]
        card.locator(".card-hover").click()
        expect(p.locator(f"#page-full-{page_id}")).to_be_visible()
        card.locator(".card-hover").click()
        expect(p.locator(f"#page-full-{page_id}")).to_be_hidden()
    finally:
        delete_wiki_page(p, title)


def test_markdown_rendered_as_html_in_expanded_view(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("MD Page ")
    try:
        create_wiki_page(p, title, content="## Heading\n\n**Bold text**")
        card = p.locator("#pages-list .card", has_text=title)
        page_id = card.get_attribute("id").split("-")[-1]
        card.locator(".card-hover").click()
        full = p.locator(f"#page-full-{page_id}")
        expect(full.locator("h2")).to_contain_text("Heading")
        expect(full.locator("strong")).to_contain_text("Bold text")
    finally:
        delete_wiki_page(p, title)


# ── Search ────────────────────────────────────────────────

def test_search_filters_pages_by_title(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    needle = uid("WikiNeedle ")
    other  = uid("WikiHay ")
    try:
        create_wiki_page(p, needle)
        create_wiki_page(p, other)
        p.locator("#search-pages").fill(needle)
        p.wait_for_timeout(400)
        expect(p.locator("#pages-list")).to_contain_text(needle)
        expect(p.locator("#pages-list")).not_to_contain_text(other)
    finally:
        p.locator("#search-pages").fill("")
        p.wait_for_timeout(400)
        delete_wiki_page(p, needle)
        delete_wiki_page(p, other)


def test_search_filters_pages_by_content(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("ContentSearch ")
    try:
        create_wiki_page(p, title, content="unique_wiki_content_marker_abc")
        p.locator("#search-pages").fill("unique_wiki_content_marker_abc")
        p.wait_for_timeout(400)
        expect(p.locator("#pages-list")).to_contain_text(title)
    finally:
        p.locator("#search-pages").fill("")
        p.wait_for_timeout(400)
        delete_wiki_page(p, title)


def test_search_clear_restores_full_page_list(logged_in_page: Page):
    p = logged_in_page
    go_to_wiki(p)
    title = uid("SearchRestore ")
    try:
        create_wiki_page(p, title)
        p.locator("#search-pages").fill("zzz_no_match_zzz")
        p.wait_for_timeout(400)
        expect(p.locator("#pages-list")).not_to_contain_text(title)
        p.locator("#search-pages").fill("")
        p.wait_for_timeout(400)
        expect(p.locator("#pages-list")).to_contain_text(title)
    finally:
        delete_wiki_page(p, title)
