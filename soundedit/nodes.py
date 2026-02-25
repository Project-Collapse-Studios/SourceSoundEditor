
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
from soundedit.utils import ConvertDataType, ConversionExists

class OperatorNode(BaseNode):
    """
    Represents a generic sound operator node
    This class is used for most sound operator nodes. At runtime it's used as the baseclass
    for a bunch of generated types for the 'real' nodes
    """

    NODE_NAME = 'Operator'
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
        print(f"Setting node name {name}")
        self.set_property("name", name, push_undo=False)
        self._register_IO()
        self._create_kv_widgets()

        # Load values from raw data
        for kv in raw_data:
            if kv.name == "operator":
                continue

            if kv.name.startswith("input") and kv.value.startswith("@"): # IO linking done after every node initializes
                continue
            
            datatype = MANIFEST.get_datatype_key(self.type, kv.name)

            value = ConvertDataType(kv.value, datatype)

            self.set_property(kv.name, value, push_undo=False)
            if self.imported:
                self.imported_data[kv.name] = value
                    

        self.initialized = True

    def _create_kv_widget(self, type_:str, name:str, *args):
        """Create a widget of type with name. Enum widgets not supported"""
        widget = None
        match type_:
            case "string":
                widget = NLineStrWidgetWrapper(self.view, name, *args)

            case "implcit_bool":
                widget = NBoolWidgetWrapper(self.view, name, *args)

            case "bool":
                widget = NBoolWidgetWrapper(self.view, name, *args)

            case "float":
                widget = NFloatWidgetWrapper(self.view, name, *args)

            case "int":
                widget = NIntWidgetWrapper(self.view, name, *args)

            case "vec3":
                widget = NVec3WidgetWrapper(self.view, name, *args)

            case "speakers":
                pass

            case "enum":
                widget = NEnumWidgetWrapper(self.view, name, *args)
                
        
        return widget

    def _create_kv_widgets(self):
        """
        Creates all input widget for specified node type
        
        Parameters
        ----------
        type : dict
            Dict representing the type
        """
        kvs = MANIFEST.keyvalue_desc(self.type)
        for kv in kvs:
            widget = None
            match kv['type']:                
                case "enum":
                    widget = self._create_kv_widget("enum", kv['name'], kv['choices'])
                    widget.set_value(self._internalgetdefault(kv['name']))

                case _:
                    widget = self._create_kv_widget(kv['type'], kv['name'])

            if widget:
                self.add_custom_widget(widget)
                    

                
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
        if self.initialized:
            raise RuntimeError("Tried to use _internalgetdefault after initialization!")
        
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
            port = self.add_output(
                name=name,
                color=MANIFEST.color_for_type(o['type'])
            )
            self.out_ports[name] = port
            

        for i in MANIFEST.input_desc(self.type):
            name = i['name']
            port = self.add_input(
                name=name,
                color=MANIFEST.color_for_type(i['type'])
            )
            self.in_ports[name] = port
            input_widget = self._create_kv_widget(i['type'], i['name'])
            if input_widget:
                self.add_custom_widget(input_widget)


        
            

    def set_property(self, name, value, push_undo = True):
        self.ImportTypeCheck()
        if name == "name":
            print("Setname called!")
        super().set_property(name, value, push_undo)

    def on_input_connected(self, in_port: Port, out_port: Port):
        """
        Called when an input is connected
        """

        # Check if port type is correct
        in_type = MANIFEST.get_port_type(self.type, 'input', in_port.name()).casefold()
        out_type = MANIFEST.get_port_type(out_port.node().type, 'output', out_port.name()).casefold()

        if not ConversionExists(out_type, in_type): # If we can't convert from them to us
            in_port.disconnect_from(out_port, push_undo=False, emit_signal=False)
            return
        
        # Handle input widget
        w: QWidget = self.get_widget(in_port.name())
        
        if not w:
            return
        
        w = w.get_custom_widget()
        #self.inputs_save[in_port.name()] = w.get_value() # NType
        w.setHidden(True) # TODO: Figure out a better way to indicate this universally for all NWidgets?
        w.setDisabled(True)

        self.ImportTypeCheck()
        return super().on_input_connected(in_port, out_port)


    def on_input_disconnected(self, in_port, out_port):
        w: QWidget = self.get_widget(in_port.name()).get_custom_widget()
        #w.setText(self.inputs_save[in_port.name()])
        w.setHidden(False)
        w.setDisabled(False)
        self.ImportTypeCheck()
        return super().on_input_disconnected(in_port, out_port)



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
        
        widgets: dict['str', QWidget] = self.widgets()
        for wid_name in widgets.keys():
            if wid_name.startswith("input"): # Inputs checked at second pass
                continue

            #print(f"Checking  property {wid_name}")

            if not wid_name in self.imported_data.keys(): # We have a custom property?
                #print(f"Custom property {wid_name}, skipping")
                continue
            
            imported_wid_data = self.imported_data[wid_name]
            if not self.get_property(wid_name) == imported_wid_data: # This automatically handles types because of N* Classes in types.py
                return False
        
        for input_port_name in self.in_ports.keys():
            input_port: Port = self.in_ports[input_port_name]
            # We're checking an input port, check if the output port remained the same
            connections = input_port.connected_ports()
            if len(connections) > 1: # Only one connection is allowed in general
                return False
            
            try:
                out_port: Port = self.imported_data[input_port_name]
            except KeyError:
                if len(connections) == 0: # If it errors, it means we didn't have a connection when imported, so check that we don't have one now
                    continue
                else:
                    return False
            
            if not out_port in connections:
                return False


        return True
            

        


    def registerImportedType(self):
        """After construction, call this to register as a locked down node (because we're an import from another operator stack)."""
        if not self.initialized:
            return
        
        if not self.imported:
            return

        self.initialized = False # Avoid recursion error
        self.set_property("color", (120, 120, 255, 255), False)
        if not self.name().startswith("IMPORTED"):
            self.set_property("name", "IMPORTED: " + self.name(), False)

        self.initialized = True

        #if not self.imported_data: # Store default data
        #    for wid_name in self.widgets():
        #        print(f"Saving property {wid_name}: {self.get_property(wid_name)}")
        #        self.imported_data[wid_name] = self.get_property(wid_name)
        
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
