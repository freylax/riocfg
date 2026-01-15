from textual.events import Key
from textual.widgets import Input, Static, RadioButton, RadioSet
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.widget import Widget
from textual.css.query import NoMatches
from halmod import get_pin,HalPin

class VelocityControl(Widget):

    FCSS = """
    VelocityControl{
        align: center top;
        /*
          Horizontal {
            margin-left: 1;               
            height: 3;
            dock: top;
        }
        */
    }
    """
    enable_pin = get_pin('rio.XAxis.enable')
    velocity_pin = get_pin('rio.XAxis.velocity')
    # def __init__(self):
    #     super().__init__(self)
        
    def compose(self) -> ComposeResult:
        assert isinstance( self.enable_pin, HalPin), "pin check"
        assert isinstance( self.velocity_pin, HalPin), "pin check"
        with Horizontal():
            yield RadioButton('[u]b[/]ack',id='bw',compact=True)
            yield RadioButton('[u]f[/]or',id='fw', compact=True)
            yield Input(type='number',compact=True)            

    def on_mount(self) -> None:
        input = self.query_one(Input)
        self.velocity_pin.read_value()
        input.value = str( self.velocity_pin.value)
        
    def on_radio_button_changed(self,m:RadioButton.Changed) -> None:
        bw = self.query_one('#bw')
        fw = self.query_one('#fw')
        input = self.query_one(Input)
        if m.control.id == 'bw' and m.control.value:
            fw.value = False;
            self.velocity_pin.write_value(- float(input.value))
            self.enable_pin.write_value(True)
        elif m.control.id == 'fw' and m.control.value:
            bw.value = False;            
            self.velocity_pin.write_value( float(input.value))
            self.enable_pin.write_value(True)
        elif not m.control.value:
            self.enable_pin.write_value(False)

    def on_key(self, ev:Key) -> None:
        def press(button_id: str) -> None:
            """Press a button, should it exist."""
            try:
                b=self.query_one(f"#{button_id}", RadioButton)
                b.focus(); b.toggle()
            except NoMatches:
                pass
        key = ev.key
        if key == 'b': press('bw')
        elif key == 'f': press('fw')
        elif not self.query_one(Input).has_focus:
            if key == 'left':
                self.app.screen.focus_previous()
            elif key == 'right':
                self.app.screen.focus_next()

    # def on_input_submitted(self,m:Input.Submitted):
    #     velocity_pin.write_value_str(m.value)
        
