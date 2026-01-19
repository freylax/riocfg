from textual.events import Key
from textual.widgets import Input, Static, RadioButton, RadioSet, Label
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.widget import Widget
from textual.css.query import NoMatches
from halmod import get_pin,HalPin,connect

class TrapVelControl(Static):

    DEFAULT_CSS = """
    TrapVelControl{
        height: 3;
        /* align: center top; */
        border: round;
        
        Horizontal {
            margin-left: 1;
            margin-right: 1;               
            height: 3;
            dock: top;
        }
        
    }
    #pos {
       width:5;
     }
    #maxv {
        width:5;
    }
    #accel {
        width:5;
    }
    """
    BORDER_TITLE = 'Velocity Control'
    
    rio_enable = get_pin('rio.XAxis.enable')
    rio_velocity = get_pin('rio.XAxis.velocity')
    rio_position = get_pin('rio.XAxis.position')
    trapvel_enable = get_pin('trapvel.enable')
    trapvel_enable_ampl = get_pin('trapvel.enable-ampl')
    trapvel_velocity = get_pin('trapvel.velocity')
    trapvel_max_velocity = get_pin('trapvel.max-velocity')
    trapvel_acceleration = get_pin('trapvel.acceleration')
    trapvel_current_pos = get_pin('trapvel.current-pos')
    trapvel_target_pos = get_pin('trapvel.target-pos')
    pins=[rio_enable,rio_velocity,rio_position,
        trapvel_enable,trapvel_enable_ampl,trapvel_velocity,
        trapvel_max_velocity, trapvel_acceleration,
        trapvel_current_pos,trapvel_target_pos]
    
    def compose(self) -> ComposeResult:
        for p in self.pins:
            assert isinstance( p, HalPin), "pin check"
        with Horizontal():
            yield RadioButton('[u]e[/]nable',id='enable',compact=True)
            yield Label('pos:')
            yield Input(type='number',max_length=5,compact=True,id='pos')
            yield Label('maxv:')
            yield Input(type='number',max_length=5,compact=True,id='maxv')
            yield Label('accel:')
            yield Input(type='number',max_length=5,compact=True,id='accel')

    def on_mount(self) -> None:
        input = self.query_one(Input)

    def activate(self) -> None:
        for p in self.pins: p.disconnect()
        connect('enable-x',self.trapvel_enable_ampl,self.rio_enable)
        connect('vel-x',self.trapvel_velocity,self.rio_velocity)
        connect('pos-x',self.rio_position,self.trapvel_current_pos)
        self.query_one('#pos',Input).value = str( self.trapvel_target_pos.value)
        self.query_one('#maxv',Input).value = str( self.trapvel_max_velocity.value)
        self.query_one( '#accel',Input).value = str( self.trapvel_acceleration.value)
        
    def on_radio_button_changed(self,m:RadioButton.Changed) -> None:
        if m.control.id == 'enable':
            self.trapvel_enable.write_value(m.control.value)

    def on_input_submitted(self,m:Input.Submitted) -> None:
        if m.input.id=='pos':
            self.trapvel_target_pos.write_value_str(m.input.value)
        elif m.input.id=='maxv':
            self.trapvel_max_velocity.write_value_str(m.input.value)
        elif m.input.id=='accel':
            self.trapvel_acceleration.write_value_str(m.input.value)

    def on_key(self, ev:Key) -> None:
        def press(button_id: str) -> None:
            """Press a button, should it exist."""
            try:
                b=self.query_one(f"#{button_id}", RadioButton)
                b.focus(); b.toggle()
            except NoMatches:
                pass
        key = ev.key
        if key == 'e': press('enable')

    



