from flask import render_template

class FrontEnd:
    def __init__(self, page_file: str):
        self._page_file = page_file

    def render_page(self):
        return render_template(self._page_file)