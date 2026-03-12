from enum import Enum


class TemplateType(str, Enum):
    STANDARD = "Standard"
    LAYOUT = "Layout"


class TemplateTypeFilter(str, Enum):
    ALL = "All"
    STANDARD = "Standard"
    LAYOUT = "Layout"


class TemplateAction(str, Enum):
    CREATE = "Create"
    EDIT = "Edit"
