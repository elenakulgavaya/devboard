import pytest
from playwright.sync_api import Page, expect
from helpers import uid, create_task, delete_task


# ── Form open / close ─────────────────────────────────────

def test_new_task_button_opens_form(logged_in_page: Page):
    p = logged_in_page
    expect(p.locator("#task-form")).to_be_hidden()
    p.locator("button", has_text="+ New Task").click()
    expect(p.locator("#task-form")).to_be_visible()


def test_cancel_button_closes_task_form(logged_in_page: Page):
    p = logged_in_page
    p.locator("button", has_text="+ New Task").click()
    p.locator("#task-form button", has_text="Cancel").click()
    expect(p.locator("#task-form")).to_be_hidden()


# ── Validation ────────────────────────────────────────────

def test_create_task_requires_title(logged_in_page: Page):
    p = logged_in_page
    p.locator("button", has_text="+ New Task").click()
    p.locator("#task-form button", has_text="Save").click()
    expect(p.locator("#task-title-err")).to_be_visible()
    expect(p.locator("#task-title-err")).to_contain_text("required")
    expect(p.locator("#task-form")).to_be_visible()  # form stays open


# ── CRUD ──────────────────────────────────────────────────

def test_create_minimal_task(logged_in_page: Page):
    p = logged_in_page
    title = uid("Task ")
    try:
        create_task(p, title)
        expect(p.locator("#task-form")).to_be_hidden()
        expect(p.locator("#tasks-list")).to_contain_text(title)
    finally:
        delete_task(p, title)


def test_create_task_with_all_fields(logged_in_page: Page):
    p = logged_in_page
    title = uid("Full Task ")
    try:
        create_task(p, title,
                    description="A detailed description",
                    labels="bug, urgent",
                    status="in_progress",
                    priority="high",
                    assignee="Alice")
        card = p.locator("#tasks-list .card", has_text=title)
        expect(card).to_contain_text("In Progress")
        expect(card).to_contain_text("high")
        expect(card).to_contain_text("Alice")
        expect(card).to_contain_text("bug")
        expect(card).to_contain_text("urgent")
    finally:
        delete_task(p, title)


def test_create_task_form_clears_after_submit(logged_in_page: Page):
    p = logged_in_page
    title = uid("Clear Test ")
    try:
        create_task(p, title, description="desc")
        p.locator("button", has_text="+ New Task").click()
        expect(p.locator("#task-title")).to_have_value("")
        expect(p.locator("#task-desc")).to_have_value("")
        p.locator("#task-form button", has_text="Cancel").click()
    finally:
        delete_task(p, title)


def test_edit_task_title(logged_in_page: Page):
    p = logged_in_page
    original = uid("Original ")
    updated  = uid("Updated ")
    try:
        create_task(p, original)
        card = p.locator("#tasks-list .card", has_text=original)
        card.locator("button[title='Edit']").click()
        p.locator("[id^='et-title-']").fill(updated)
        p.locator(".card", has_text="Editing task #").locator("button", has_text="Save").click()
        expect(p.locator("#tasks-list")).to_contain_text(updated)
        expect(p.locator("#tasks-list")).not_to_contain_text(original)
    finally:
        delete_task(p, updated)


def test_edit_task_cancel_restores_original(logged_in_page: Page):
    p = logged_in_page
    title = uid("Stable Task ")
    try:
        create_task(p, title)
        card = p.locator("#tasks-list .card", has_text=title)
        card.locator("button[title='Edit']").click()
        p.locator("[id^='et-title-']").fill("Should not appear")
        p.locator(".card", has_text="Editing task #").locator("button", has_text="Cancel").click()
        expect(p.locator("#tasks-list")).to_contain_text(title)
        expect(p.locator("#tasks-list")).not_to_contain_text("Should not appear")
    finally:
        delete_task(p, title)


def test_delete_task(logged_in_page: Page):
    p = logged_in_page
    title = uid("Delete Me ")
    create_task(p, title)
    delete_task(p, title)
    expect(p.locator("#tasks-list")).not_to_contain_text(title)


# ── Status cycling ────────────────────────────────────────

def test_cycle_status_todo_to_in_progress(logged_in_page: Page):
    p = logged_in_page
    title = uid("Cycle ")
    try:
        create_task(p, title, status="todo")
        card = p.locator("#tasks-list .card", has_text=title)
        card.locator(".badge-todo").click()
        expect(card.locator(".badge-in_progress")).to_be_visible()
    finally:
        delete_task(p, title)


def test_cycle_status_in_progress_to_done(logged_in_page: Page):
    p = logged_in_page
    title = uid("Cycle2 ")
    try:
        create_task(p, title, status="in_progress")
        card = p.locator("#tasks-list .card", has_text=title)
        card.locator(".badge-in_progress").click()
        expect(card.locator(".badge-done")).to_be_visible()
    finally:
        delete_task(p, title)


def test_cycle_status_wraps_done_back_to_todo(logged_in_page: Page):
    p = logged_in_page
    title = uid("Wrap ")
    try:
        create_task(p, title, status="done")
        card = p.locator("#tasks-list .card", has_text=title)
        card.locator(".badge-done").click()
        expect(card.locator(".badge-todo")).to_be_visible()
    finally:
        delete_task(p, title)


# ── Filter tabs ───────────────────────────────────────────

def test_filter_todo_shows_only_todo_tasks(logged_in_page: Page):
    p = logged_in_page
    todo_title = uid("FilterTodo ")
    done_title = uid("FilterDone ")
    try:
        create_task(p, todo_title, status="todo")
        create_task(p, done_title, status="done")
        p.locator("#filter-todo").click()
        expect(p.locator("#tasks-list")).to_contain_text(todo_title)
        expect(p.locator("#tasks-list")).not_to_contain_text(done_title)
    finally:
        p.locator("#filter-all").click()
        delete_task(p, todo_title)
        delete_task(p, done_title)


def test_filter_done_shows_only_done_tasks(logged_in_page: Page):
    p = logged_in_page
    todo_title = uid("FDone_todo ")
    done_title = uid("FDone_done ")
    try:
        create_task(p, todo_title, status="todo")
        create_task(p, done_title, status="done")
        p.locator("#filter-done").click()
        expect(p.locator("#tasks-list")).to_contain_text(done_title)
        expect(p.locator("#tasks-list")).not_to_contain_text(todo_title)
    finally:
        p.locator("#filter-all").click()
        delete_task(p, todo_title)
        delete_task(p, done_title)


def test_overdue_filter_shows_past_due_tasks(logged_in_page: Page):
    p = logged_in_page
    title = uid("Overdue ")
    try:
        p.locator("button", has_text="+ New Task").click()
        p.locator("#task-title").fill(title)
        p.locator("#task-due-at").fill("2020-01-01T00:00")
        p.locator("#task-form button", has_text="Save").click()
        expect(p.locator("#tasks-list")).to_contain_text(title)
        p.locator("#filter-overdue").click()
        expect(p.locator("#tasks-list")).to_contain_text(title)
    finally:
        p.locator("#filter-all").click()
        delete_task(p, title)


# ── Search ────────────────────────────────────────────────

def test_search_filters_tasks_by_title(logged_in_page: Page):
    p = logged_in_page
    needle = uid("Needle ")
    other  = uid("Haystack ")
    try:
        create_task(p, needle)
        create_task(p, other)
        p.locator("#search-tasks").fill(needle)
        p.wait_for_timeout(400)  # debounce
        expect(p.locator("#tasks-list")).to_contain_text(needle)
        expect(p.locator("#tasks-list")).not_to_contain_text(other)
    finally:
        p.locator("#search-tasks").fill("")
        p.wait_for_timeout(400)
        delete_task(p, needle)
        delete_task(p, other)


def test_search_filters_tasks_by_description(logged_in_page: Page):
    p = logged_in_page
    title = uid("DescSearch ")
    try:
        create_task(p, title, description="unique_desc_marker_xyz")
        p.locator("#search-tasks").fill("unique_desc_marker_xyz")
        p.wait_for_timeout(400)
        expect(p.locator("#tasks-list")).to_contain_text(title)
    finally:
        p.locator("#search-tasks").fill("")
        p.wait_for_timeout(400)
        delete_task(p, title)


def test_search_clear_restores_full_list(logged_in_page: Page):
    p = logged_in_page
    title = uid("SearchClear ")
    try:
        create_task(p, title)
        p.locator("#search-tasks").fill("zzz_no_match_zzz")
        p.wait_for_timeout(400)
        expect(p.locator("#tasks-list")).not_to_contain_text(title)
        p.locator("#search-tasks").fill("")
        p.wait_for_timeout(400)
        expect(p.locator("#tasks-list")).to_contain_text(title)
    finally:
        delete_task(p, title)


# ── Comments ──────────────────────────────────────────────

def test_add_comment_to_task(logged_in_page: Page):
    p = logged_in_page
    title = uid("Comment Task ")
    try:
        create_task(p, title)
        card = p.locator("#tasks-list .card", has_text=title)
        card.locator("button", has_text="Comments").click()

        card_id = card.get_attribute("id").split("-")[-1]
        p.locator(f"#comment-author-{card_id}").fill("Tester")
        p.locator(f"#comment-content-{card_id}").fill("This is a test comment")
        card.locator("button", has_text="Post").click()

        expect(p.locator(f"#comments-list-{card_id}")).to_contain_text("Tester")
        expect(p.locator(f"#comments-list-{card_id}")).to_contain_text("This is a test comment")
    finally:
        delete_task(p, title)


def test_comment_requires_author_and_content(logged_in_page: Page):
    p = logged_in_page
    title = uid("CommentVal ")
    try:
        create_task(p, title)
        card = p.locator("#tasks-list .card", has_text=title)
        card.locator("button", has_text="Comments").click()
        card.locator("button", has_text="Post").click()

        card_id = card.get_attribute("id").split("-")[-1]
        expect(p.locator(f"#comment-author-{card_id}-err")).to_be_visible()
        expect(p.locator(f"#comment-content-{card_id}-err")).to_be_visible()
    finally:
        delete_task(p, title)


# ── History ───────────────────────────────────────────────

def test_task_history_recorded_after_edit(logged_in_page: Page):
    p = logged_in_page
    original = uid("HistOrig ")
    updated  = uid("HistNew ")
    try:
        create_task(p, original)
        card = p.locator("#tasks-list .card", has_text=original)
        card.locator("button[title='Edit']").click()
        p.locator("[id^='et-title-']").fill(updated)
        p.locator(".card", has_text="Editing task #").locator("button", has_text="Save").click()
        expect(p.locator("#tasks-list")).to_contain_text(updated)

        card = p.locator("#tasks-list .card", has_text=updated)
        card.locator("button", has_text="History").click()
        card_id = card.get_attribute("id").split("-")[-1]
        expect(p.locator(f"#history-list-{card_id}")).to_contain_text(original)
        expect(p.locator(f"#history-list-{card_id}")).to_contain_text(updated)
    finally:
        delete_task(p, updated)


# ── Draft ─────────────────────────────────────────────────

def test_task_draft_auto_saved_to_localstorage(logged_in_page: Page):
    p = logged_in_page
    draft_title = uid("Draft ")
    p.locator("button", has_text="+ New Task").click()
    p.locator("#task-title").fill(draft_title)
    p.locator("#task-desc").fill("draft body")
    p.wait_for_timeout(200)
    draft = p.evaluate("() => JSON.parse(localStorage.getItem('devboard_task_draft') || '{}')")
    assert draft.get("title") == draft_title
    assert draft.get("description") == "draft body"
    p.locator("#task-form button", has_text="Cancel").click()


def test_draft_cleared_on_cancel(logged_in_page: Page):
    p = logged_in_page
    p.locator("button", has_text="+ New Task").click()
    p.locator("#task-title").fill(uid("Draft "))
    p.locator("#task-form button", has_text="Cancel").click()
    draft = p.evaluate("() => localStorage.getItem('devboard_task_draft')")
    assert draft is None
