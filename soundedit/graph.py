from NodeGraphQt import (
    NodeGraph, BaseNode, Port,
    NodeGraphMenu, NodesMenu,
)
from NodeGraphQt.widgets.node_graph import NodeGraphWidget
from PySide6.QtWidgets import (
    QTabWidget, QHBoxLayout, QMenu
)
from PySide6.QtCore import QObject
from PySide6.QtGui import QCursor
from PySide6 import QtCore

from soundedit import manifest, nodes, types
from soundedit.nodes import (
    OperatorNode, FloatConstNode
)
from srctools import Keyvalues

from typing import (
    Tuple, TypedDict, Dict, Any
)


class SoundOperatorGraph(QObject):
    """
    Main graph for the sound editor
    Registers all required node types and manages the editor
    """

    def __init__(self, parent):
        super().__init__()
        self.nodes: Dict[str, OperatorNode] = {}
        self.graph = NodeGraph(self)
        # Register all node types
        for type in manifest.node_types().keys():
            self.graph.register_node(
                OperatorNode(type).__class__
            )

        self.graph.register_node(
            FloatConstNode
        )

        self._dirty = False

        # Configure our context menus. These are static for some reason
        self._build_graph_context_menu()
        self._build_node_context_menu()

        self.graph.property_changed.connect(lambda: self.mark_dirty())
        self.graph.node_created.connect(lambda: self.mark_dirty())
        self.graph.nodes_deleted.connect(lambda: self.mark_dirty())
        self.graph.port_connected.connect(lambda: self.mark_dirty())
        self.graph.port_disconnected.connect(lambda: self.mark_dirty())

    """Signaled when the dirty flag has been changed"""
    dirty_changed = QtCore.Signal(bool)

    def mark_dirty(self, dirty: bool = True, signal: bool = False) -> None:
        """
        Mark the dirty flag, signals the changed() event

        Parameters
        ----------
        dirty : bool
            True if dirty
        """
        self._dirty = dirty
        self.dirty_changed.emit(dirty)

    @property
    def widget(self) -> NodeGraphWidget:
        return self.graph.widget

    def dirty(self) -> bool:
        """Returns the status of the dirty flag"""
        return self._dirty

    def load_stack(self, opstack: Keyvalues, all_opstacks: Keyvalues):
        """
        Load an operator stack from a dict
        
        Parameters
        ----------
        opstack : Keyvalues
            The operator stack to load.
        """
        # Pass 0: find all import_stacks
        # TODO: Handling for this should be improved. import_stack's are a bit funny, they basically merge keyvalues sections
        #  for now we're just merging with no regard for the output. Not sure how else you'd represent this in the graph anyway
            
        for imp in opstack.find_all("import_stack"):
            imported_stack = all_opstacks.find_block(imp.value)
            for op in imported_stack:
                print(f"Merging {op.real_name}!")
                op_name = op.real_name
                if op_name in opstack:
                    our_operator = opstack.find_block(op_name)
                    for kv in op:
                        key = kv.real_name
                        if not key in our_operator:
                            our_operator[key] = kv.value
                else:
                    opstack.append(op)
            

        # Pass 1: create all nodes
        for node in opstack:
            if node.has_children():
                self._create_node(node)
            else:
                print('WARNING: unhandled import_stack operator')
                print(f'{node}')

        # Pass 2: resolve connections
        #for node in opstack.keys():
        #    value = opstack[node]
        #    if isinstance(value, dict):
        #        self._resolve(node, opstack)

        self.graph.auto_layout_nodes()

    def make_node(self, node_type: str, name: str | None = None) -> OperatorNode:
        """
        Makes a new node, setting defaults as required
        
        Parameters
        ----------
        node_type : str
            Node type, shorthand version (i.e. math_clamp)
        name : str | None
            Name of the node when added to the graph (i.e. my_node)
            If not provided, a unique name will be generated based on the operator type
            
        Returns
        -------
        OperatorNode :
            New node
        """
        if name is None:
            name = self.graph.get_unique_name(node_type)

        n: OperatorNode = self.graph.create_node(
            f'io.soundedit.operators.Operator_{node_type}',
            name=name
        )
        n.set_type(node_type)
        self.nodes[name] = n
        self.set_defaults(n)
        return n

    def set_defaults(self, node: OperatorNode) -> None:
        """Set default keyvalues on the node"""
        for kv in manifest.current().keyvalue_desc(node.type):
            node.set_widget_value(kv['name'], kv['default'])

    def _create_node(self, node: Keyvalues):
        """
        Creates a new named node from existing operator stack data
        
        Parameters
        ----------
        nodeName : str
            Name of the node
        opstack : Keyvalues
            Keyvalues of operator stack data
        """
        if node.name == "import_stack": # Skip imported stacks
            return

        print(node)
        operator = node['operator']
        n = self.make_node(operator, node.real_name)

        # Create any constant nodes
        constNodeNum = 0
        for input in manifest.current().input_desc(operator):
            inpName = input['name']
            if not inpName in node:
                continue

            value: str = node[inpName]
            port: Port = n.get_input_port(inpName)
            if value.startswith('@'):
                continue
            
            n.set_input_const(inpName, value)
            
        # Set keyvalues
        for kv in manifest.current().keyvalue_desc(operator):
            if kv['name'] not in node:
                continue
            n.set_widget_value(kv['name'], node[kv['name']])

    def _resolve(self, nodeName: str, opstack):
        """
        Resolves inter-node references
        
        Parameters
        ----------
        nodeName : str
            Name of the node
        opstack : VDFDict
            Dictionary of operator stack data
        """
        operator = opstack[nodeName]['operator']
        node = opstack[nodeName]
        
        for input in manifest.current().input_desc(operator):
            inputName = input['name']
            if not inputName in node or not node[inputName].startswith('@'):
                continue
            
            value: str = node[inputName]
            otherName, outName = self._split_input_str(value)
            
            other: OperatorNode = self.nodes[otherName]
            p: Port = other.get_output_port(outName)
            i: Port = self.nodes[nodeName].get_input_port(inputName)
            p.connect_to(
                i,
                push_undo=False
            )

    def _split_input_str(self, value: str) -> Tuple[str, str]: # (nodeName, outputName)
        value = value.removeprefix('@')
        vals = value.split('.')
        return (vals[0], vals[1])

    def remove_node(self, name: str) -> bool:
        """
        Remove a node by name
        
        Parameters
        ----------
        name : str
            Remove a unique node by its name
        
        Returns
        -------
        bool :
            True on success
        """
        if name not in self.nodes:
            return False
        n = self.nodes.pop(name)
        self.graph.delete_node(n)
        return True

    def _add_node(self, type: str) -> None:
        node = self.make_node(type, type)
        self.graph.add_node(
            node, QCursor.pos()
        )

    def _build_graph_context_menu(self):
        """Add new entries to the graph context menu"""
        menu: NodeGraphMenu = self.graph.get_context_menu('graph')

        # Add node menu
        m = menu.add_menu('Add Node')
        subs = {x: m.add_menu(x) for x in manifest.current().categories()}
        for k, v in manifest.node_types().items():
            if k == '__base': continue # Skip the "base" node
            x = subs[v['category']] if 'category' in v else m
            x.add_command(
                k, lambda graph: self._add_node(k)
            )

        menu.add_command(
            'Auto-layout',
            lambda graph: graph.auto_layout_nodes()
        )

    def _build_node_context_menu(self):
        """Add new entries to the node context menus"""
        menu: NodesMenu = self.graph.get_context_menu('nodes')
        menu.add_command(
            'Remove Node',
            lambda graph, node: graph.remove_node(node.name()),
            node_class=BaseNode
        )
        
        def do_reset_def(graph, node):
            if getattr(node, '__identifier__', None) != OperatorNode.__identifier__:
                return
            graph.begin_undo('Reset to defaults')
            graph.set_defaults(node)
            graph.end_undo()

        menu.add_command(
            'Reset to Defaults',
            lambda graph, node: do_reset_def(graph, node),
            node_class=BaseNode
        )
