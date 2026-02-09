"""Houses node widgets for N* types"""

from soundedit.types import *
from PySide6.QtWidgets import QCheckBox

class NBoolWidget(QCheckBox):
    """Checkbox like widget"""
    def __init__(self, ):
        super().__init__()
