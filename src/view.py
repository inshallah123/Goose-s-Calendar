import flet as ft
from viewmodels import PageViewModel


class PageView: # 定义pageview
    def __init__(self, page: ft.Page, viewmodel: PageViewModel):
        self.page = page
        self.viewmodel = viewmodel
        self.content_container = None
        self._ctrl_pressed = False
        self.viewmodel.set_property_changed_callback(self._on_viewmodel_changed)
        self._apply_properties()

    
    def _apply_properties(self):
        self.page.title = self.viewmodel.title
        self.page.bgcolor = self.viewmodel.bgcolor
        
        if self.viewmodel.width:
            self.page.window_width = self.viewmodel.width
        if self.viewmodel.height:
            self.page.window_height = self.viewmodel.height

        self.page.window_resizable = self.viewmodel.auto_resize

        self.page.update()
    
    def set_content_container(self, container):
        self.content_container = container
    
    def _on_viewmodel_changed(self):
        self._apply_properties() # #

