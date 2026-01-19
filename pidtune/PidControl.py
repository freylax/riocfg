from textual.events import Key
from textual.widgets import Input, Static, RadioButton, RadioSet, Label
from textual.containers import Horizontal
from textual.app import ComposeResult
from textual.widget import Widget
from textual.css.query import NoMatches
from halmod import get_pin,HalPin,connect

class PidControl(Static):

    DEFAULT_CSS = """
    PidControl{
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
    BORDER_TITLE = 'Pid Control'
    
    rio_enable = get_pin('rio.XAxis.enable')
    rio_velocity = get_pin('rio.XAxis.velocity')
    rio_position = get_pin('rio.XAxis.position')
    pid_enable = get_pin('pid.enable')
    pid_command = get_pin('pid.command')
    pid_feedback = get_pin('pid.feedback')
    pid_output = get_pin('pid.output')
    pid_maxoutput = get_pin('pid.maxoutput')
    pins=[rio_enable,rio_velocity,rio_position,
        pid_enable,pid_command,pid_feedback,
        pid_output, pid_maxoutput]
    
    def compose(self) -> ComposeResult:
        for p in self.pins:
            assert isinstance( p, HalPin), "pin check"
        with Horizontal():
            yield RadioButton('[u]e[/]nable',id='enable',compact=True)
            yield Label('pos:')
            yield Input(type='number',max_length=5,compact=True,id='pos')
            yield Label('maxv:')
            yield Input(type='number',max_length=5,compact=True,id='maxv')
            # yield Label('accel:')
            # yield Input(type='number',max_length=5,compact=True,id='accel')

    def on_mount(self) -> None:
        input = self.query_one(Input)

    def deactivate(self) -> None:
        for p in self.pins: p.disconnect()

    def activate(self) -> None:
        connect('vel-x',self.pid_output,self.rio_velocity)
        connect('pos-x',self.rio_position,self.pid_feedback)
        self.pid_command.read_value()
        self.pid_maxoutput.read_value()
        self.query_one('#pos',Input).value = str( self.pid_command.value)
        self.query_one('#maxv',Input).value = str( self.pid_maxoutput.value)
        
    def on_radio_button_changed(self,m:RadioButton.Changed) -> None:
        if m.control.id == 'enable':
            self.rio_enable.write_value(m.control.value)
            self.pid_enable.write_value(m.control.value)
            
    def on_input_submitted(self,m:Input.Submitted) -> None:
        if m.input.id=='pos':
            self.pid_command.write_value_str(m.input.value)
        elif m.input.id=='maxv':
            self.pid_maxoutput.write_value_str(m.input.value)
        # elif m.input.id=='accel':
            # self.trapvel_acceleration.write_value_str(m.input.value)

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

    



