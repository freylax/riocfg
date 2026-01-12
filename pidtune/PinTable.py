from textual.worker import get_current_worker
from textual.coordinate import Coordinate
from textual.message import Message
from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.reactive import reactive
from textual import log, work
from rich.text import Text

from halmod import PinDir, PinType, HalPin

def pin_val_to_cell( p:HalPin) -> Text:
    if p.value is None: return Text(text='---')
    match p.type:
        case PinType.BOOL:
            if p.value: return Text.from_markup(':new_moon:')
            else: return Text.from_markup(':full_moon:')
        case PinType.U32:
            return Text(text=str(p.value))
        case PinType.S32:
            return Text(text=str(p.value))
        case PinType.FLOAT:
            return Text(text=str(p.value))
    return Text(text='---')

class PinTable(DataTable):
    """Display HalPins"""

    class Selected(Message):
        """Pin Selected Message"""    
        pin: tuple[int, HalPin]

        def __init__(self,pin: tuple[int,HalPin]) -> None:
            self.pin=pin
            super().__init__()
            
    pins:list[HalPin]=reactive([])

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        self.add_columns("Pin", "Value")
        self.set_interval(1,self.update_pins)
        
    def on_data_table_row_selected(self, m:DataTable.RowSelected)->None:
        pin=self.pins[m.cursor_row]
        if pin.dir is PinDir.IN:
            if pin.type is PinType.BOOL:
                # just toggle the pin
                self.update_cell_at( Coordinate(m.cursor_row,1),value="---")
                pin.write_value(not pin.value)
            else:
                self.post_message(self.Selected((m.cursor_row,pin)))
                
    def watch_pins( self, pins:list[HalPin] ) -> None:
        self.clear()
        for pin in pins:
           self.add_row(pin.name,pin_val_to_cell(pin))

    @work(exclusive=True, thread=True)
    def update_pins(self) -> None:
        worker = get_current_worker()
        for row,pin in enumerate(self.pins):
            if pin.read_value():
                coord = Coordinate( row,1)
                v = pin_val_to_cell(pin)
                if not worker.is_cancelled:
                    self.app.call_from_thread( self.update_cell_at,coord,value=v)
    
