#!/usr/bin/env python3
from typing import Iterable
from textual.screen import Screen

from textual.app import App,ComposeResult, SystemCommand
from textual.widgets import Footer, Header, Label, Input, DataTable, TabbedContent, TabPane, RichLog
from textual.containers import Vertical,Horizontal
from textual import log

from PinTable import PinTable
from PinInput import PinInput
from VelocityControl import VelocityControl
from TrapVelControl import TrapVelControl
from halmod import get_pins

import linuxcnc


class PidTuneApp(App):
    CSS = """
    PidTuneApp {
        PinTable {
            width:50%
        }
    }  
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal():
            yield PinTable()
            with TabbedContent():
                with TabPane("VeloCtrl",id="velctrl"):
                    yield VelocityControl()
                with TabPane("TrapVel",id='trapvel'):
                    yield TrapVelControl()
                with TabPane("Log",id='log'):
                    yield RichLog()
        yield Footer()

    def on_mount(self) -> None:
        log('main.on_mount')
        self.load_pins()

    def load_pins(self) -> None:
        t = self.query_one(PinTable)
        t.pins = get_pins( ['trapvel','rio.sys-enable','rio.XAxis'])
         
    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)  
        yield SystemCommand("load", "load pins", self.load_pins)

    def on_tabbed_content_tab_activated(self, m:TabbedContent.TabActivated) -> None:
        tab_id = m.tab.id
        if tab_id.endswith('velctrl'):
            self.query_one(VelocityControl).activate()
        elif tab_id.endswith('trapvel'): 
            tc = self.query_one( TrapVelControl)
            vc = self.query_one( VelocityControl)
            tc.activate()
            l = self.query_one(RichLog)
            l.write(f"sig:{tc.trapvel_current_pos.signal},{vc.rio_pos.signal}")
         
    # def on_pin_table_selected(self, m:PinTable.Selected)->None:
    #     input = self.query_one(PinInput)
    #     input.pin = m.pin
    #     self.set_focus(input,scroll_visible=True)

#    def on_input_submitted(self, message:Input.Submitted)->None:
        

if __name__ == "__main__":
    app = PidTuneApp()
    app.run()
