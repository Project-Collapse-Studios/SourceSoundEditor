from soundedit.types import *

def ConvertDataType(val: str, type: str):
    match type:
            case "bool":
                return NBool(val)
            
            case "implicit_bool":
                return NBool(val)

            case "str":
                return NStr(val)
            
            case "string":
                return NStr(val)
            
            case "enum":
                return NEnumVal(val)
            
            case "float":
                return NFloat(val)
            
            case "vec3":
                return NVec3.from_str(val)
            
            case "speakers":
                return NSpeakers(val)

            case _:
                return None
                raise RuntimeError(f"Unknown data type {type}!")
        

def ConversionExists(type1: str, type2: str) -> bool:
    """Returns true/false depending on if conversion from type1 onto type2 exists"""
    if type1 == type2:
        return True
    
    if type1 in ("bool", "implicit_bool"):
        if type2 in ("implicit_bool", "str", "string"):
            return True
        
    if type1 == "str" and type2 == "string":
        return True
        
    if type1 == "string" and type2 == "str":
        return True
    
    if type1 == "int":
        if type2 in ("bool", "implicit_bool", "str", "string", "float"):
            return True
        
    if type1 == "float":
        if type2 in ("bool", "implicit_bool", "str", "string"):
            return True
        

    return False