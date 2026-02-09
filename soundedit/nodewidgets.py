"""Houses node widgets for N* types"""

from soundedit.types import *
from PySide6.QtWidgets import QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit, QWidget, QLabel, QGridLayout, QComboBox
from NodeGraphQt import NodeBaseWidget

MAX_VAL_SPINBOX = 9999999999

class NBoolWidget(QCheckBox):
    """Checkbox like widget"""

    TYPE = NBool

    def __init__(self, text, *arg):
        super().__init__(text = text, *arg, tristate=False)

    def get_value(self):
        return NBool(self.isChecked())
    
    def set_value(self, val: NBool):
        self.setChecked(val.value)

class NBoolWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None, name=None):
        super(NBoolWidgetWrapper, self).__init__(parent, name)
        self.set_custom_widget(NBoolWidget(text=name))

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NBool):
        self.get_custom_widget().set_value(value)     

class NIntWidget(QSpinBox):
    """Spinbox like widget"""

    TYPE = NInt

    def __init__(self, *args):
        super().__init__(*args)
        self.setRange(-MAX_VAL_SPINBOX, MAX_VAL_SPINBOX)

    def get_value(self):
        return NInt(self.value())
    
    def set_value(self, val: NInt):
        self.setValue(val.value)

class NIntWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None, name=None):
        super(NIntWidgetWrapper, self).__init__(parent, name)
       
        self.set_custom_widget(NIntWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NInt):
        self.get_custom_widget().set_value(value)   

class NFloatWidget(QDoubleSpinBox):
    """DoubleSpinbox like widget"""

    TYPE = NFloat

    def __init__(self, *args):
        super().__init__(*args)
        self.setDecimals(10)
        self.setRange(-MAX_VAL_SPINBOX, MAX_VAL_SPINBOX)

    def get_value(self):
        return NFloat(self.value())
    
    def set_value(self, val: NFloat):
        self.setValue(val.value)

class NFloatWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None, name=None):
        super(NFloatWidgetWrapper, self).__init__(parent, name)
       
        self.set_custom_widget(NFloatWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NFloat):
        self.get_custom_widget().set_value(value)    

class NLineStrWidget(QLineEdit):
    """DoubleSpinbox like widget"""

    TYPE = NStr

    def get_value(self):
        return NStr(self.text())
    
    def set_value(self, val: NStr):
        self.setText(val.value)

class NLineStrWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None, name=None):
        super(NLineStrWidgetWrapper, self).__init__(parent, name)
       
        self.set_custom_widget(NLineStrWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NStr):
        self.get_custom_widget().set_value(value)    


class NMultiLineStrWidget(QTextEdit):
    """DoubleSpinbox like widget"""

    TYPE = NStr

    def get_value(self):
        return NStr(self.toPlainText())
    
    def set_value(self, val: NStr):
        self.setPlainText(val.value)

class NMultiLineStrWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None, name=None):
        super(NMultiLineStrWidgetWrapper, self).__init__(parent, name)
       
        self.set_custom_widget(NMultiLineStrWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NStr):
        self.get_custom_widget().set_value(value)   

class NVec3Widget(QWidget):
    """DoubleSpinbox like widget"""

    xBox:QDoubleSpinBox
    yBox:QDoubleSpinBox
    zBox:QDoubleSpinBox

    TYPE = NVec3

    def __init__(self, *arg):
        super().__init__(*arg)
        layout = QGridLayout(self)

        xLabel = QLabel("X:",self)
        layout.addWidget(xLabel,0,0)
        self.xBox = QDoubleSpinBox(self)
        layout.addWidget(self.xBox,0,1)
        yLabel = QLabel("Y:",self)
        layout.addWidget(yLabel,1,0)
        self.yBox = QDoubleSpinBox(self)
        layout.addWidget(self.yBox,1,1)
        zLabel = QLabel("Z:",self)
        layout.addWidget(zLabel,2,0)
        self.zBox = QDoubleSpinBox(self)
        layout.addWidget(self.zBox,2,1)


    def get_value(self):
        return NVec3(self.xBox.value(), self.yBox.value(), self.zBox.value())
    
    def set_value(self, val: NVec3):
        self.xBox.setValue(val.get_x())
        self.xBox.setValue(val.get_y())
        self.xBox.setValue(val.get_z())

class NVec3WidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None, name=None):
        super(NVec3WidgetWrapper, self).__init__(parent, name)
       
        self.set_custom_widget(NVec3Widget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NVec3):
        self.get_custom_widget().set_value(value)


class NEnumWidget(QComboBox):
    """Combo box widget"""
    
    TYPE = NEnumVal

    def get_value(self):
        return NEnumVal(self.currentText())
    
    def set_value(self, val: NEnumVal):
        self.setCurrentText(val.value)

class NEnumWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None, name=None, *args):
        super().__init__(parent, name)

        widget = NEnumWidget(
            editable=False,

        )
        self.set_custom_widget(widget)
        widget.addItems(args[0])

    def get_value(self):
        return self.get_custom_widget().get_value()
    
    def set_value(self, value: NEnumVal):
        self.get_custom_widget().set_value(value)