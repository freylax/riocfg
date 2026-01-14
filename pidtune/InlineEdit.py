from textual.app import App, ComposeResult
from textual.message import Message
from textual.widgets import DataTable, Input
from textual.coordinate import Coordinate
from textual.reactive import reactive
from textual.geometry import Offset

ROWS = [
    ("lane", "swimmer", "country", "time"),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (5, "Chad le Clos", "South Africa", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
    (10, "Darren Burns", "Scotland", 51.84),
]

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

class TableApp(App):
        
    def compose(self) -> ComposeResult:
        yield DataTable()
        yield DataInput()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])
        input = self.query_one(DataInput)
        input.styles.position = 'absolute'
        input.styles.offset=(0,0)
        input.display = False
        
    def on_data_table_cell_selected( self, m:DataTable.CellSelected) -> None:
        input = self.query_one(DataInput)
        if input.display is True:
            # we do not want successive edits if a mouse
            # click selects another cell if we were editing
            input.display = False
            return
        table = self.query_one(DataTable)
        # calculate the position of the input widget
        c = m.coordinate
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
        input.value = str(m.value)
        input.coord = m.coordinate
        input.display = True
        input.focus()
        
    def on_data_input_value_submitted(self, m:DataInput.ValueSubmitted) -> None:
        input = self.query_one(DataInput)
        input.display = False
        table = self.query_one(DataTable)
        table.update_cell_at( m.coord, value=m.value)

    def on_data_input_blurred(self, m:DataInput.Blurred) -> None:
        input = self.query_one(DataInput)
        input.display = False
    
                
app = TableApp()
if __name__ == "__main__":
    app.run()
