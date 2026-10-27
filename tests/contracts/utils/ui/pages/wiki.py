from surety.diff import compare
from surety.ui import Button, Container, Label, TextInput
from surety.ui.browser import Elements

from tests.contracts.utils.ui.pages.base import BasePage


def page_to_ui_dict(page, is_full=False):
    content = page.Content.value.replace('\n', ' ')

    if len(content) > 180:
        content = content[:180] + '…'

    return {
        'title': f'📄 {page.Title.value}',
        'content': '' if is_full else content,
        'full_page': page.Content.value if is_full else '',
    }


class NewPageForm(Container):
    Title = TextInput(css='#page-title')
    TitleError = Label(css='#page-title-err')
    Content = TextInput(css='#page-content')

    SaveButton = Button(css='button[onclick^=submitPage]')
    CancelButton = Button(css='button[onclick^=closePageForm]')


class PageCard(Container):
    Title = Label(css='p.font-semibold')
    Content = Label(css='p.font-mono')
    FullPage = Label(css='div[id*=page-full]')
    EditButton = Button(css='button[onclick*=startEditPage]')
    DeleteButton = Button(css='button[onclick*=deletePage]')


    EditHeader = Label(css='p.font-semibold')
    TitleEdit = TextInput(css='input[id*=ep-title]')
    ContentEdit = TextInput(css='textarea[id*=ep-content]')

    SaveButton = Button(css='button[onclick^=saveEditPage]')
    CancelButton = Button(css='button[onclick^=cancelEditPage]')


    def to_dict(self):
        full_page_text = ''

        if self.FullPage.is_present():
            full_page_text = self.FullPage.text

        return {
            'title': self.Title.text,
            'content': self.Content.text,
            'full_page': full_page_text,
        }


class PagesList(Container):
    Cards = Elements(css='div.card', element_class=PageCard)

    @property
    def pages(self):
        return [page.to_dict() for page in self.Cards]

    def verify_pages(self, pages, is_full=False):
        self.Cards.wait_for_items_load(len(pages))
        compare(
            actual=self.pages,
            expected=[page_to_ui_dict(page, is_full=is_full) for page in pages],
            target_name='pages list'
        )


class WikiPage(BasePage):
    NewPageButton = Button(css='button[onclick^=openPageForm]')
    SearchInput = TextInput(css='#search-pages')

    NewPage = NewPageForm(css='#page-form')
    PagesList = PagesList(css='#pages-list')

    AllTasks = Button(css='#filter-all')
    TodoTasks = Button(css='#filter-todo')
    InProgressTasks = Button(css='#filter-in_progress')
    DoneTasks = Button(css='#filter-done')
    OverdueTasks = Button(css='#filter-overdue')
