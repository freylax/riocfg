from textual.widget import Widget
from textual.events import Key
from textual.worker import get_current_worker
from textual.coordinate import Coordinate
from textual.message import Message
from textual.app import ComposeResult
from textual.widgets import Static, DataTable, Input
from textual.reactive import reactive
from textual.coordinate import Coordinate
from textual import log, work
from textual.geometry import Offset
from rich.text import Text

from halmod import PinDir, PinType, HalPin

pin_on  = Text.from_markup(':new_moon:',justify='left')
pin_off = Text.from_markup(':full_moon:',justify='left')    
dir_in  = Text.from_markup(':right_arrow_curving_left:',justify='right',style="green") 
dir_out = Text.from_markup(':left_arrow_curving_right:',justify='right') 
dir_in_con = Text.from_markup(':zap::right_arrow_curving_left:',justify='right') 
dir_out_con = Text.from_markup(':zap::left_arrow_curving_right:',justify='right') 
dir_in_out = Text.from_markup(':zap::left_right_arrow:',justify='right') 

class DataInput(Input):
    """Our cell edit widget, leave with return or escape"""
    BINDINGS = Input.BINDINGS.append(("escape","abort()","abort edit"))
    coord = reactive(Coordinate(0,0))

    class ValueSubmitted(Message):
        value:str
        coord:Coordinate
        def __init__(self,value:str,coord:Coordinate) -> None:
            self.value=value
            self.coord=coord
            super().__init__()
    def __init__(self):
        super().__init__(compact=True)
        self.display=False
    def on_input_submitted(self, m:Input.Submitted) -> None:
        self.post_message(self.ValueSubmitted(m.value,self.coord))
    def action_abort(self) -> None:
        self.display = False

def pin_val_to_cell( p:HalPin) -> Text:
    if p.value is None: return Text(text='---')
    match p.type:
        case PinType.BOOL:
            if p.value: return pin_on
            else: return pin_off
        case PinType.U32:
            return Text(text=str(p.value))
        case PinType.S32:
            return Text(text=str(p.value))
        case PinType.FLOAT:
            return Text(text=str(p.value))
    return Text(text='---')

def pin_dir_to_cell( p:HalPin) -> Text:
    match p.dir:
        case PinDir.IN:
            if p.signal is None: return dir_in
            else: return dir_in_con    
        case PinDir.OUT:
            if p.signal is None: return dir_out
            else: return dir_out_con
        case PinDir.IN_OUT: return dir_in_out
        
class PinTable(Widget):
    """Display HalPins"""
    
    class Selected(Message):
        """Pin Selected Message"""    
        pin: tuple[int, HalPin]

        def __init__(self,pin: tuple[int,HalPin]) -> None:
            self.pin=pin
            super().__init__()
            
    pins:list[HalPin]=reactive([])

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield DataInput()

    def on_mount(self) -> None:
        table= self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        self.column_keys = table.add_columns(('Pin','pin'),(dir_in_out,'dir'),('Value','value'),
                                             ('Signal','signal'))
        self.set_interval(1,self.update_pins)
        input = self.query_one(DataInput)
        input.display = False
        input.styles.position = 'absolute'
        input.styles.offset=(0,0)
 
    def on_data_table_row_selected(self, m:DataTable.RowSelected)->None:
        input = self.query_one(DataInput)
        table = self.query_one(DataTable)
        if input.display is True:
            # we do not want successive edits if a mouse
            # click selects another cell if we were editing
            input.display = False
            return
        pin=self.pins[m.cursor_row]
        if pin.dir is PinDir.OUT: return
        if isinstance( pin.signal, str): return
        val_idx = table.get_column_index('value')
        c = Coordinate(row=m.cursor_row,column=val_idx)
        if pin.type is PinType.BOOL:
            # just toggle the pin
            table.update_cell_at( c,value='---')
            pin.write_value(not pin.value)
            return
        # self.post_message(self.Selected((m.cursor_row,pin)))
        # calculate the position of the input widget
        x = table.cell_padding   # x offset
        y = table.header_height  # y offset
        w = 0                    # width of input widget
        for i,col in enumerate(table.ordered_columns):
            if i < c.column:
                x += col.get_render_width(table)
            else:
                w = col.content_width 
                break
        co = table.content_offset
        so = table.scroll_offset
        x += co.x - so.x
        y += co.y + c.row - so.y 
        input.offset = Offset(x,y)
        input.styles.width = w
        input.value = str(pin.value)
        input.coord = c
        input.display = True
        input.focus()

    def on_key(self,ev:Key) -> None:
        if(ev.key=='space'):
            table = self.query_one(DataTable)
            pin=self.pins[table.cursor_row]
            if pin.dir is PinDir.OUT: return
            if isinstance(pin.signal,str): return
            val_idx = table.get_column_index('value')
            c = Coordinate(row=table.cursor_row,column=val_idx)
            if pin.type is PinType.BOOL:
                # just toggle the pin
                table.update_cell_at( c,value='---')
                pin.write_value(not pin.value)
        
    def on_data_input_value_submitted(self, m:DataInput.ValueSubmitted) -> None:
        pin=self.pins[m.coord.row]
        input = self.query_one(DataInput)
        input.display = False
        table = self.query_one(DataTable)
        table.update_cell_at( m.coord, value='---')
        pin.write_value_str( m.value)

    def on_data_input_blurred(self, m:DataInput.Blurred) -> None:
        input = self.query_one(DataInput)
        input.display = False

    def watch_pins( self, pins:list[HalPin] ) -> None:
        k=self.column_keys
        assert k[0].value == 'pin' and k[1].value == 'dir' and k[2].value == 'value', "column key mismatch"
        table = self.query_one(DataTable)
        table.clear()
        for pin in pins:
           table.add_row(pin.name,pin_dir_to_cell(pin),pin_val_to_cell(pin))

    @work(exclusive=True, thread=True)
    def update_pins(self) -> None:
        table = self.query_one(DataTable)
        worker = get_current_worker()
        for row,pin in enumerate(self.pins):
            if pin.read_value():
                val_idx = table.get_column_index('value')
                val_crd = Coordinate( row, val_idx)
                v = pin_val_to_cell(pin)
                if not worker.is_cancelled:
                    self.app.call_from_thread( table.update_cell_at,val_crd,value=v)
            dir_idx = table.get_column_index('dir')
            dir_crd = Coordinate( row, dir_idx)
            sig_idx = table.get_column_index('signal')
            sig_crd = Coordinate( row, sig_idx)
            d = pin_dir_to_cell(pin)
            s =''
            if isinstance(pin.signal,str): s=pin.signal
            if not worker.is_cancelled:
                self.app.call_from_thread( table.update_cell_at,dir_crd,value=d)
                self.app.call_from_thread( table.update_cell_at,sig_crd,value=s)
                    
