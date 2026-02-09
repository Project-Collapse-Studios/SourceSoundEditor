
from NodeGraphQt import (
    BaseNode, Port
)
from NodeGraphQt.widgets.node_widgets import (
    NodeLineEdit, NodeBaseWidget, NodeComboBox, NodeCheckBox
)

from PySide6.QtWidgets import (
    QLineEdit
)
from PySide6.QtGui import (
    QDoubleValidator
)

from soundedit.manifest import MANIFEST
from .types import NodeKeyValueType
from srctools import conv_bool, Keyvalues
from soundedit.nodewidgets import *

class OperatorNode(BaseNode):
    """
    Represents a generic sound operator node
    This class is used for most sound operator nodes. At runtime it's used as the baseclass
    for a bunch of generated types for the 'real' nodes
    """

    NODE_NAME = 'new operator'
    __identifier__ = 'io.soundedit.operators'


    def __init__(self, type_: str|None, name:str, raw_data: bool, imported:bool):
        super().__init__()
        self.in_ports = {}
        self.out_ports = {}
        self.type = type_
        self.initialized = False # Set to true if we're finished with setting ourselves up

        self.imported = imported # Set to true if we're a node that belongs to another op stack and we've been imported onto this one
        self.imported_data: dict = {} # Stores the data to compare with, if we can un-unregister ourselves

        self.inputs_save = {} # Saves data in input widgets for when they are disconnected

        self.set_property("name", name, push_undo=False)
        self._register_IO()
        self._create_kv_widgets()

        # Load values from raw data
        for kv in raw_data:
            if kv.name == "operator":
                continue
            
            if kv.name.startswith("input") and kv.value.startswith("@"): # TODO: handle input linking
                continue
            
            
            datatype = MANIFEST.get_datatype_key(self.type, kv.name)

            #TODO:FIX
            #print(f"Val: {kv.value}, converted to: {val}")
            #self.set_property(kv.name, val, push_undo=False)
            #if self.imported:
            #    self.imported_data[kv.name] = (val, val_type)

        self.initialized = True



    def _create_kv_widgets(self):
        """
        Create input widget for specified type
        
        Parameters
        ----------
        type : dict
            Dict representing the type
        """
        kvs = MANIFEST.keyvalue_desc(self.type)
        for kv in kvs:
            widget = None
            match kv['type']:
                case "string":
                    widget = NLineStrWidgetWrapper(self.view, kv['name'])

                case "implcit_bool":
                    widget = NBoolWidgetWrapper(self.view, kv['name'])

                case "bool":
                    widget = NBoolWidgetWrapper(self.view, kv['name'])

                case "float":
                    widget = NFloatWidgetWrapper(self.view, kv['name'])

                case "int":
                    widget = NIntWidgetWrapper(self.view, kv['name'])

                case "vec3":
                    widget = NVec3WidgetWrapper(self.view, kv['name'])

                case "speakers":
                    pass

                case "enum":
                    self.add_combo_menu(
                        name=kv['name'],
                        label=kv['name'],
                        items=kv['choices']
                    )
                    self.set_property(kv['name'], str(self._internalgetdefault(kv['name']).value), push_undo=False)

                case _:
                    pass
                    #raise RuntimeError(f"Unknown data type {kv['type']}")

            if widget:
                self.add_custom_widget(widget)
                    

        #for kv in kvs:
        #    match kv['type']:
        #        case 'string':
        #            self.add_text_input(
        #                name=kv['name'],
        #                label=kv['name'],
        #                text=self._internalgetdefault(kv['name'])
        #            )
        #        case 'implicit_bool':
        #            self.add_checkbox(
        #                name=kv['name'],
        #                label=kv['name'],
        #                state=self._internalgetdefault(kv['name'])
        #            )
        #        case 'bool':
        #            self.add_checkbox(
        #                name=kv['name'],
        #                label=kv['name'],
        #                state=self._internalgetdefault(kv['name'])
        #            )
        #        case 'enum':
        #            self.add_combo_menu(
        #                name=kv['name'],
        #                label=kv['name'],
        #                items=kv['choices']
        #            )
        #            self.set_property(kv['name'], self._internalgetdefault(kv['name']), push_undo=False)

                
    def set_widget_value(self, widget_name: str, value: str) -> bool:
        """
        Set a named widget's value
        
        Parameters
        ----------
        widget_name : str
            Name of the widget to lookup
        value : str
            Value of the widget. This will be automatically converted to the required type depending on the widget
        """
        raise RuntimeError("Tried to use set_widget_value!")
        w: NodeBaseWidget = self.get_widget(widget_name)
        if w is None:
            return False

        if isinstance(w, NodeCheckBox):
            w.set_value(conv_bool(value))
        else:
            w.set_value(value)
        return True

    def _internalgetdefault(self, key):
        """Internal function, gets the default of a keyvalue and saves it internally if we're an imported node, to compare with later"""
        val = MANIFEST.get_default(self.type, key)
        self.imported_data[key] = val
        return val


    def _register_IO(self):
        """
        Sets the node type
        This will create all input and output ports, and any embedded widgets
        
        Parameters
        ----------
        type : str
            Name of the backing node type, looked up within the manifest
        """
        for o in MANIFEST.output_desc(self.type):
            name = o['name']
            self.out_ports[name] = self.add_output(
                name=name,
                color=MANIFEST.color_for_type(o['type'])
            )

        for i in MANIFEST.input_desc(self.type):
            name = i['name']
            self.in_ports[name] = self.add_input(
                name=name,
                color=MANIFEST.color_for_type(i['type'])
            )
            self.add_text_input(
                name=name,
                label=name,
                tab=name,
                text=str(self._internalgetdefault(name).value) #TODO: Handle better
            )
            

    def set_property(self, name, value, push_undo = True):
        self.ImportTypeCheck()
        super().set_property(name, value, push_undo)


    def on_input_connected(self, in_port: Port, out_port: Port):
        """
        Called when an input is connected
        """
        w: QLineEdit = self.get_widget(in_port.name()).get_custom_widget()
        self.inputs_save[in_port.name()] = w.text()
        w.setText("<CONNECTION>")
        w.setDisabled(True)
        self.ImportTypeCheck()
        return super().on_input_connected(in_port, out_port)


    def on_input_disconnected(self, in_port, out_port):
        w: QLineEdit = self.get_widget(in_port.name()).get_custom_widget()
        w.setText(self.inputs_save[in_port.name()])
        w.setDisabled(False)
        self.ImportTypeCheck()
        return super().on_input_disconnected(in_port, out_port)


    def set_input_const(self, input: str, value: str):
        """
        Set an input constant for the specified input
        This will set the line edit's value
        
        Parameters
        ----------
        input : str
            Input name
        value : str
            Value text
        """
        w: QLineEdit = self.get_widget(input).get_custom_widget()
        w.setText(value)



    def get_input_port(self, name: str) -> Port:
        return self.in_ports[name]
        
        
    def get_output_port(self, name: str) -> Port:
        return self.out_ports[name]


    #def __new__(metacls, typ: str|None = None):
    #    """
    #    Returns new instance of OperatorNode.
    #    Generates a new metatype with a unique name so we can use this single class
    #    for multiple node types, dynamically added via the manifest.
    #    
    #    Parameters
    #    ----------
    #    typ : str
    #        The type of the operator node
    #    """
    #    if typ is not None:
    #        # Generate new type
    #        metacls = type(f'Operator_{typ}', (OperatorNode,), {
    #            'opType_': typ,
    #            '__identifier__': f'io.soundedit.operators'
    #        })
    #    
    #    c = object.__new__(metacls)
    #    return c

    def ImportTypeCheck(self):
        if not self.initialized: # We're still in the phase of setting ourselves up.
            return

        if not self._tryRegisterImportedType():
            self.unregisterImportedType()
        else:
            self.imported = True
            self.registerImportedType()

    def _tryRegisterImportedType(self):
        if not self.imported_data: # We have never been an imported node
            return False
        
        widgets: dict = self.widgets()
        for wid_name in widgets.keys():
            print(f"Checking  property {wid_name}")
            #if wid_name.startswith("input"): #TODO: handle inputs
            #    continue

            if not wid_name in self.imported_data: # We have a custom property?
                print(f"Custom property {wid_name}, skipping")
                continue
            
            # Try converting to bool, as a custom field
            #TODO: REFACTOR THIS CODE
            try:
                conversion1 = conv_bool(self.imported_data[wid_name], default="FAILED")
                conversion2 = conv_bool(self.get_property(wid_name), default="FAILED")
                if conversion1 == "FAILED" or conversion2 == "FAILED":
                    raise RuntimeError # Will get properly handled
                
                if not conversion1 == conversion2: # Else we've converted properly, and this is a bool value
                    return False
            except:
                if not self.imported_data[wid_name] == self.get_property(wid_name):
                    print(f"IData: {self.imported_data[wid_name]}")
                    print(f"PData: {self.get_property(wid_name)}")
                    return False

        return True
            

        


    def registerImportedType(self):
        """After construction, call this to register as a locked down node (because we're an import from another operator stack)."""
        if not self.initialized:
            return
        
        if not self.imported:
            return
        
        self.set_property("color", (120, 120, 255, 255), False)
        if not self.name().startswith("IMPORTED"):
            self.set_property("name", "IMPORTED: " + self.name(), False)

        if not self.imported_data: # Store default data
            for wid_name in self.widgets():
                print(f"Saving property {wid_name}: {self.get_property(wid_name)}")
                self.imported_data[wid_name] = self.get_property(wid_name)
        
    def unregisterImportedType(self):
        """Called whenever anything in this node (besides output) changes. Unregisters the imported type and adds us to the operator stack."""
        if not self.initialized:
            return
        
        if not self.imported: # We've either already been unregistered or never have been
            return 
        self.imported = False

        self.set_color(0, 0, 0)
        self.set_name(self.name().replace("IMPORTED: ", ""))


class FloatConstNode(BaseNode):
    """A node that is simply a float constant"""
    
    __identifier__ = 'io.soundedit.consts'
    NODE_NAME = 'float const'
    
    def __init__(self):
        super().__init__()
        
        self.outPort_ = self.add_output(
            name='output',
            color=MANIFEST.color_for_type('float')
        )
        
        self.add_text_input(
            name='value',
            label='value',
            text='1.0'
        )
        
        edit: QLineEdit = self.get_widget('value').get_custom_widget()
        edit.setValidator(QDoubleValidator(edit))


    def set_value(self, value: str):
        edit: QLineEdit = self.get_widget('value').get_custom_widget()
        edit.setText(value)


    def get_output_port(self):
        return self.outPort_
