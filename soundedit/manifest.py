
import json
import os

from typing import Tuple, Dict

from soundedit.types import *
from srctools import conv_bool



class Manifest:
    """
    A game-specific manifest
    Describes all available nodes, their inputs, outputs and keyvalues
    """
    def __init__(self, file: str):
        self.manifest = file
        self._categories = set()
        self._load_manifest()

    def _load_manifest(self) -> None:
        with open(self.manifest, 'r') as fp:
            self.nodes: dict = json.load(fp)
            self.baseNode = self.node_type('__base')
            
            if self.baseNode is None:
                return

            # Unify __base with all other node types
            for k in self.nodes.keys():
                if k == '__base':
                    continue
                n = self.nodes[k]
                n['keyvalues'] += self.baseNode['keyvalues']
                n['outputs'] += self.baseNode['outputs']
                n['inputs'] += self.baseNode['inputs']
                if 'category' in n:
                    self._categories.add(n['category'])
                self.nodes[k] = n

    def node_type(self, type_: str) -> NodeType|None:
        return self.node_types()[type_] if type_ in self.node_types() else None

    def node_types(self) -> Dict[str, NodeType]:
        return self.nodes

    def input_desc(self, type_: str) -> list[NodeInputType]:
        return self.nodes[type_]['inputs']

    def output_desc(self, type_: str) -> list[NodeOutputType]:
        return self.nodes[type_]['outputs']

    def keyvalue_desc(self, type_: str) -> list[NodeKeyValueType]:
        return self.nodes[type_]['keyvalues']

    def categories(self) -> set[str]:
        return self._categories
    
    @staticmethod
    def color_for_type(type: str) -> Tuple[int, int, int]:
        match type:
            case 'vec3':
                return (0, 255, 0)
            case 'float':
                return (255, 255, 0)
            case 'speakers':
                return (255, 0, 0)
            case 'vec3x8':
                return (255, 0, 255)
            case _:
                raise Exception('Invalid type name')
            
    def node_types(self) -> Dict[str, NodeType]:
        return self.nodes
    
    def get_datatype_key(self, nodetype: str, key: str) -> str:
        """Get the datatype of a keyvalue by nodetype and key"""
        if key.startswith("input"): # Inputs are in a different part of the datastructure
            kv_desc = self.input_desc(nodetype)
        else:
            kv_desc = self.keyvalue_desc(nodetype)

        for kv in kv_desc:
            if key.casefold() == kv['name'].casefold():
                    return kv['type']

    
    def get_default(self, nodetype: str, key: str):
        """Get the default value of key from operator type of nodetype. Returns a tuple (value, value type)"""
        if key.startswith("input"): # Inputs are in a different part of the datastructure
            kv_desc = self.input_desc(nodetype)
        else:
            kv_desc = self.keyvalue_desc(nodetype)

        val = None
        valtype = None
        for kv in kv_desc:
            if key.casefold() == kv['name'].casefold():
                valtype = kv['type']
                try:
                    val = kv['default']
                except KeyError:
                    val = ""
        
        if val == None:
            raise RuntimeError(f"Cannot find default value for operator type {nodetype}: {key}")
        
        match valtype:
            case "bool":
                return NBool(val)
            
            case "implcit_bool":
                return NBool(val)

            case "str":
                return NStr(val)
            
            case "string":
                return NStr(val)
            
            case "enum": # Enums are just fancy strings
                return NEnumVal(val)
            
            case "float": # Floats also get mapped to str, because there is not Float input box (yet at least)
                return NFloat(val)
            
            case "vec3":
                return NVec3.from_str(val)
            
            case "speakers":
                return NSpeakers(val)

            case _:
                raise RuntimeError(f"Unknown data type {valtype}!")
        
            
    

                
GAMES = {
    'strata': Manifest(os.path.dirname(__file__) + '/games/strata.json')
}
MANIFEST = GAMES['strata']


def load_manifest(name: str):
    global _current
    _current = GAMES[name]



