from xml.etree.ElementTree import ElementTree

from surety.diff import compare
from surety.ui import Button, Container, Label, TextInput
from surety.ui.browser import Elements

from tests.contracts.utils.ui.pages.base import BasePage


class NewPageForm(Container):
    Title = TextInput(css='#page-title')
    TitleError = Label(css='#page-title-err')
    Content = TextInput(css='#page-content')

    SaveButton = Button(css='button[onclick^=submitPage]')
    CancelButton = Button(css='button[onclick^=closePageForm]')


class PageCard(Container):
    Title = Label(css='p.font-semibold')
    FullPage = Label(css='div[id*=page-full]>div.md-body')
    EditButton = Button(css='button[onclick*=startEditPage]')
    DeleteButton = Button(css='button[onclick*=deletePage]')
    PageTasks = Elements(css='div[id*=page-tasks]>div', element_class=Label)

    EditHeader = Label(css='p.font-semibold')
    TitleEdit = TextInput(css='input[id*=ep-title]')
    ContentEdit = TextInput(css='textarea[id*=ep-content]')

    SaveButton = Button(css='button[onclick^=saveEditPage]')
    CancelButton = Button(css='button[onclick^=cancelEditPage]')

    def verify_page(self, page, tasks):
        def task_to_label(task):
            status = task.Status.value.replace('_', ' ').title()
            return f'{status}\n{task.Priority.value}\n{task.Title.value}'

        actual = {
            'title': self.Title.text,
            'full_content': self.FullPage.text if self.FullPage.is_present() else None,
            'tasks': self.PageTasks.get_labels(),
        }
        compare(
            actual=actual,
            expected={
                'title': f'📄 {page.Title.value}',
                'full_content': page.Content.value,
                'tasks': [task_to_label(task) for task in tasks],
            }
        )



class PagesList(Container):
    Cards = Elements(css='div.card', element_class=PageCard)

    @property
    def pages(self):
        return [page.Title.text for page in self.Cards]

    def verify_pages(self, pages):
        self.Cards.wait_for_items_load(len(pages))
        compare(
            actual=self.pages,
            expected=[f'📄 {page.Title.value}' for page in pages],
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
