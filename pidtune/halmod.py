from enum import Enum
from typing import NamedTuple, TypeVar
import hal

class PinDir(Enum):
    IN = hal.HAL_IN
    OUT = hal.HAL_OUT
    IN_OUT = hal.HAL_IN | hal.HAL_OUT # used for testing
        
class PinType(Enum):
    BOOL = hal.HAL_BIT
    U32 = hal.HAL_U32
    S32 = hal.HAL_S32
    FLOAT = hal.HAL_FLOAT

Value=TypeVar('Value', None,bool,int,float)
    
def create_HalPin_value(t:PinType,value):#None | bool | int | float:
    if value is None:
        return None
    match t:
        case PinType.BOOL:
            return bool(value)
        case PinType.U32:
            return value
        case PinType.S32:
            return value
        case PinType.FLOAT:
            return float(value)
    return None # to get type checker pleased

class HalPin:
    name: str
    dir: PinDir
    type: PinType
    # value: Value
    def __init__(self,name: str,dir:PinDir,type:PinType,value):
        self.name = name
        self.dir = dir
        self.type = type
        self._value = create_HalPin_value(type,value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value:Value):
        self._value = value   

    def read_value(self) -> bool:
        """Update the pin value by request the value of the hal pin.
        Return True if changed, False otherwise."""
        v = create_HalPin_value(self.type,hal.get_value(self.name))
        if v != self.value:
            self.value=v
            return True
        else: return False

    def write_value(self, value:Value)-> None:
        """Write the given pin value to the hal.
        This does not alter the current value of this object.
        Call read_value to update the value form the hal """        
        hal.set_p(self.name,str(value))        

    def write_value_str(self, value:str)-> None:
        """Write the given pin value provided as string to the hal.
        This does not alter the current value of this object.
        Call read_value to update the value form the hal """        
        hal.set_p(self.name,value)        

def dict_to_HalPin(d:dict) -> HalPin:
    return HalPin(
        name = str(d.get('NAME')),
        dir = PinDir(d.get('DIRECTION')),
        type= PinType(d.get('TYPE')),
        value= d.get('VALUE'))

_ini_component = None

def check_initialized() -> None:
    global _ini_component
    if _ini_component is None:
        _ini_component = hal.component("halmod_init") 

_hal_pins = None
         
def get_all_pins(reread:bool=False) -> list[HalPin]:
    check_initialized()
    global _hal_pins
    if _hal_pins is None or reread:
        _hal_pins = list(map(dict_to_HalPin,hal.get_info_pins()))
    return _hal_pins   


def get_pins(select:list[str], dir:PinDir=PinDir.IN_OUT, reread:bool=False)->list[HalPin]:
    pins = get_all_pins(reread)
    l = []
    for s in select:
        for p in pins:
            if p.name.startswith(s) and p.dir.value & dir.value == p.dir.value:
                l.append(p)
    return l

def get_pin(name:str, reread:bool=False) -> HalPin | None:
    pins = get_all_pins(reread)
    for p in pins:
        if p.name == name:
            return p
    return None
