from enum import Enum
from typing import NamedTuple
import hal

class PinDir(Enum):
    IN = hal.HAL_IN
    OUT = hal.HAL_OUT
        
class PinType(Enum):
    BOOL = hal.HAL_BIT
    U32 = hal.HAL_U32
    S32 = hal.HAL_S32
    FLOAT = hal.HAL_FLOAT
    

class HalPin(NamedTuple):
    dir: PinDir
    type: PinType
    val: bool | int | float

def create_HalPin_value(t:PinType,val) -> bool | int | float:
    match t:
        case PinType.BOOL:
            return bool(val)
        case PinType.U32,PinType.S32:
            return int(val)
        case PinType.FLOAT:
            return float(val)
    return False # to get type checker pleased

def dict_to_HalPin(d:dict) -> tuple[str,HalPin]:
    t = PinType(d.get('TYPE'))
    return ( str(d.get('NAME')),
            HalPin(
            dir = PinDir(d.get('DIRECTION')),
            type= t,
            val= create_HalPin_value(t,d.get('VALUE'))))
         
def get_hal_pins() -> dict[str,HalPin]:
    l = hal.get_info_pins()
    return dict( map(dict_to_HalPin,l))
        
    
      
