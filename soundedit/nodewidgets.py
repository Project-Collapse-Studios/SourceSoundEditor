"""Houses node widgets for N* types"""

from soundedit.types import *
from PySide6.QtWidgets import QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit, QWidget, QLabel, QGridLayout
from NodeGraphQt import NodeBaseWidget

class NBoolWidget(QCheckBox):
    """Checkbox like widget"""
    def __init__(self, *arg):
        super().__init__(arg, tristate=False)

    def get_value(self):
        return NBool(self.isChecked())
    
    def set_value(self, val: NBool):
        self.setChecked(val.value)

class NBoolWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NBoolWidgetWrapper, self).__init__(parent)
        self.set_custom_widget(NBoolWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NBool):
        self.get_custom_widget().set_value(value.value)     

class NIntWidget(QSpinBox):
    """Spinbox like widget"""

    def get_value(self):
        return NInt(self.value())
    
    def set_value(self, val: NInt):
        self.setValue(val.value)

class NIntWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NIntWidgetWrapper, self).__init__(parent)
       
        self.set_custom_widget(NIntWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NInt):
        self.get_custom_widget().set_value(value.value)   

class NFloatWidget(QDoubleSpinBox):
    """DoubleSpinbox like widget"""

    def get_value(self):
        return NFloat(self.value())
    
    def set_value(self, val: NFloat):
        self.setValue(val.value)

class NFloatWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NFloatWidgetWrapper, self).__init__(parent)
       
        self.set_custom_widget(NFloatWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NFloat):
        self.get_custom_widget().set_value(value.value)    

class NLineStrWidget(QLineEdit):
    """DoubleSpinbox like widget"""

    def get_value(self):
        return NStr(self.text())
    
    def set_value(self, val: NStr):
        self.setText(val.value)

class NLineStrWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NLineStrWidgetWrapper, self).__init__(parent)
       
        self.set_custom_widget(NLineStrWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NStr):
        self.get_custom_widget().set_value(value.value)    


class NMultiLineStrWidget(QTextEdit):
    """DoubleSpinbox like widget"""

    def get_value(self):
        return NStr(self.toPlainText())
    
    def set_value(self, val: NStr):
        self.setPlainText(val.value)

class NMultiLineStrWidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NMultiLineStrWidgetWrapper, self).__init__(parent)
       
        self.set_custom_widget(NMultiLineStrWidget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NStr):
        self.get_custom_widget().set_value(value.value)   

class NVec3Widget(QWidget):
    """DoubleSpinbox like widget"""

    xBox:QDoubleSpinBox
    yBox:QDoubleSpinBox
    zBox:QDoubleSpinBox

    def __init__(self, *arg):
        super().__init__(arg)
        layout = QGridLayout(self)

        xLabel = QLabel("X:",self)
        layout.addWidget(xLabel,0,0)
        xBox = QDoubleSpinBox(self)
        layout.addWidget(xBox,0,1)
        yLabel = QLabel("Y:",self)
        layout.addWidget(yLabel,1,0)
        yBox = QDoubleSpinBox(self)
        layout.addWidget(yBox,1,1)
        zLabel = QLabel("Z:",self)
        layout.addWidget(zLabel,2,0)
        zBox = QDoubleSpinBox(self)
        layout.addWidget(zBox,2,1)


    def get_value(self):
        return NVec3(self.xBox.value(), self.yBox.value(), self.zBox.value())
    
    def set_value(self, val: NVec3):
        self.xBox.setValue(val.get_x().value)
        self.xBox.setValue(val.get_y().value)
        self.xBox.setValue(val.get_z().value)

class NVec3WidgetWrapper(NodeBaseWidget):
    def __init__(self, parent=None):
        super(NVec3WidgetWrapper, self).__init__(parent)
       
        self.set_custom_widget(NVec3Widget())

    def get_value(self):
        return self.get_custom_widget().get_value()

    def set_value(self, value: NVec3):
        self.get_custom_widget().set_value(value.get_xyz())   