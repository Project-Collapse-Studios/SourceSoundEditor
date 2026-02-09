
from typing import TypedDict, Literal, Dict
import enum
from srctools import conv_bool, conv_float, conv_int
class StackType(enum.IntEnum):
    Start = 0,
    Update = 1,
    Stop = 2



class NodeKeyValueType(TypedDict):
    """
    Describes a single key value for a node
    """
    name: str
    type: Literal['bool', 'float', 'int', 'implcit_bool', 'enum']
    choices: list[str]|None
    default: str
    

class NodeIOType(TypedDict):
    """
    Describes an input or output for a node
    """
    name: str
    type: Literal['float', 'vec3', 'vec3x8', 'speakers']
    default: str
    

class NodeInputType(NodeIOType):
    """
    An input -- Unique type from NodeIOType to be more specific
    """
    pass


class NodeOutputType(NodeIOType):
    """
    An output -- Unique type from NodeIOType to be more specific
    """
    pass


class NodeType(TypedDict):
    """
    Describes a node's key values, inputs, outputs and any additional info
    """
    label: str
    desc: str|None
    inputs: list[NodeInputType]
    outputs: list[NodeOutputType]
    keyvalues: list[NodeKeyValueType]


class NodeManifest(TypedDict):
    """
    The node manifest
    """
    game: str
    nodes: Dict[str, NodeType]
    


# DATA TYPES
# That can be in a value of a sound operator
class NBool:
    """Represents a boolean"""
    def __init__(self, val, def_ = False):
        self.value = conv_bool(val, default=def_)

class NInt:
    """Represents an integer"""
    def __init__(self, val, def_ = 0):
        self.value = conv_int(val, default=def_)

class NFloat:
    """Represents a float"""
    def __init__(self, val, def_ = 0):
        self.value = conv_float(val, default=def_)

class NStr:
    """Represents a string"""
    def __init__(self, val):
        self.value = val

class NEnumVal:
    """Represents an enum value"""
    def __init__(self, val):
        self.value = val

class NVec3:
    """Represents a 3D Vector"""

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.value = f"[{self.x} {self.y} {self.z}]"

    @staticmethod
    def from_str(s: str):
        try:
            x, y, z = s.split(" ")
        except ValueError:
            x, y, z = 0, 0, 0 #TODO: Implement undefined behaviour
        
        return NVec3(float(x), float(y), float(z))

    
    def get_xyz(self):
        return (self.x,self.y,self.z)

    def get_x(self) -> float:
        return self.x

    def get_y(self) -> float:
        return self.y
    
    def get_z(self) -> float:
        return self.z


class NSpeakers:
    """Represents speakers"""
    def __init__(self, val):
        self.value = val