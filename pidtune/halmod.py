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

# mapping of pin names to signals
_pin_signals = []

def set_pin_signal(pin_name:str,signal:str):
    global _pin_signals
    for s in _pin_signals:
        if s[0] == pin_name:
            s[1] = str;
            return
    _pin_signals.append((pin_name,signal))
    return None

def get_pin_signal(pin_name:str):
    global _pin_signals
    for s in _pin_signals:
        if s[0] == pin_name:
            return s[1]
    return None

def remove_pin_signal(pin_name:str):
    global _pin_signals
    for i, s in enumerate(_pin_signals):
        if s[0] == pin_name:
            _pin_signals.pop(i)
            return

class HalPin:
    name: str
    dir: PinDir
    type: PinType
    # value: Value
    # signal: None | str
    def __init__(self,name: str,dir:PinDir,type:PinType,value,signal:None | str):
        self.name = name
        self.dir = dir
        self.type = type
        self._value = create_HalPin_value(type,value)
        self._signal = signal
        
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value:Value):
        self._value = value   

    @property
    def signal(self) -> str|None:
        return self._signal
        #return get_pin_signal(self.name)

    @signal.setter
    def signal(self, signal:str|None):
        self._signal = signal
        # if signal is None:
        #     remove_pin_signal(self.name)
        # else:
        #     set_pin_signal(self.name, signal)   

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

    def connect(self, signal:str)-> None:
        hal.disconnect(self.name)
        hal.connect(self.name,signal)
        self.signal = signal

    def disconnect(self)-> None:
        hal.disconnect(self.name)
        self.signal = None

def create_signal(signal:str,type:PinType)-> None:
    signals = hal.get_info_signals()
    if not next(filter(lambda x:x['NAME']==signal,signals),False):
        hal.new_sig(signal,type.value)

def connect(signal:str,*pins)-> None:
    create_signal(signal,pins[0].type)
    for p in pins:
        p.connect(signal)


def dict_to_HalPin(d:dict) -> HalPin:
    return HalPin(
        name = str(d.get('NAME')),
        dir = PinDir(d.get('DIRECTION')),
        type= PinType(d.get('TYPE')),
        value= d.get('VALUE'),
        signal= d.get('SIGNAL'))

_ini_component = None

def check_initialized() -> None:
    global _ini_component
    if _ini_component is None:
        for i in range(10):
            try:
                _ini_component = hal.component(f"halmod_init{i}")
                break 
            except hal.error:
                continue
                
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
