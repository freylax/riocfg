#!/usr/bin/env python3
from typing import Iterable
from textual.screen import Screen

from textual.app import App,ComposeResult, SystemCommand
from textual.widgets import Footer, Header, Label, Input, DataTable
from textual.containers import Vertical,Horizontal
from textual import log

from PinTable import PinTable
from PinInput import PinInput
from PidTuner import VelocityControl
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
            yield VelocityControl()
        yield Footer()

    def on_mount(self) -> None:
        log('main.on_mount')
        self.load_pins()

    def load_pins(self) -> None:
        t = self.query_one(PinTable)
        t.pins = get_pins( ['rio.sys-enable','rio.XAxis'])
         
    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)  
        yield SystemCommand("load", "load pins", self.load_pins)  

    # def on_pin_table_selected(self, m:PinTable.Selected)->None:
    #     input = self.query_one(PinInput)
    #     input.pin = m.pin
    #     self.set_focus(input,scroll_visible=True)

#    def on_input_submitted(self, message:Input.Submitted)->None:
        

if __name__ == "__main__":
    app = PidTuneApp()
    app.run()
