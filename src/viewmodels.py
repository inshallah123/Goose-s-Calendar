
from typing import Callable, Optional

class PageViewModel:
    def __init__(self):
        self._width: Optional[int] = None
        self._height: Optional[int] = None
        self._title: str = "日历应用"
        self._bgcolor: str = "#ffffff"
        self._auto_resize: bool = True
        self._zoom_factor: float = 1.0
        self._min_zoom: float = 0.5
        self._max_zoom: float = 3.0
        self._zoom_step: float = 0.1
        self._on_property_changed: Optional[Callable] = None
    
    @property
    def width(self) -> Optional[int]:
        return self._width
    
    @width.setter
    def width(self, value: Optional[int]):
        if self._width != value:
            self._width = value
            self._notify_change()
    
    @property
    def height(self) -> Optional[int]:
        return self._height
    
    @height.setter
    def height(self, value: Optional[int]):
        if self._height != value:
            self._height = value
            self._notify_change()
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str):
        if self._title != value:
            self._title = value
            self._notify_change()
    
    @property
    def bgcolor(self) -> str:
        return self._bgcolor
    
    @bgcolor.setter
    def bgcolor(self, value: str):
        if self._bgcolor != value:
            self._bgcolor = value
            self._notify_change()
    
    @property
    def auto_resize(self) -> bool:
        return self._auto_resize
    
    @auto_resize.setter
    def auto_resize(self, value: bool):
        if self._auto_resize != value:
            self._auto_resize = value
            self._notify_change()
    
    @property
    def zoom_factor(self) -> float:
        return self._zoom_factor

    @property
    def min_zoom(self) -> float:
        return self._min_zoom
    
    @property
    def max_zoom(self) -> float:
        return self._max_zoom
    
    def set_property_changed_callback(self, callback: Callable):
        self._on_property_changed = callback
    
    def _notify_change(self):
        if self._on_property_changed:
            self._on_property_changed()
