```python
from IPython.display import HTML
import random

def hide_toggle(for_next=False):
    this_cell = """$('div.cell.code_cell.rendered.selected')"""
    next_cell = this_cell + '.next()'

    toggle_text = 'Toggle show/hide'  # text shown on toggle link
    target_cell = this_cell  # target cell to control with toggle
    js_hide_current = ''  # bit of JS to permanently hide code in current cell (only when toggling next cell)

    if for_next:
        target_cell = next_cell
        toggle_text += ' next cell'
        js_hide_current = this_cell + '.find("div.input").hide();'

    js_f_name = 'code_toggle_{}'.format(str(random.randint(1,2**64)))

    html = """
        <script>
            function {f_name}() {{
                {cell_selector}.find('div.input').toggle();
            }}

            {js_hide_current}
        </script>

        <a href="javascript:{f_name}()">{toggle_text}</a>
    """.format(
        f_name=js_f_name,
        cell_selector=target_cell,
        js_hide_current=js_hide_current, 
        toggle_text=toggle_text
    )

    return HTML(html)

hide_toggle()
```





<script>
    function code_toggle_7120154357069289297() {
        $('div.cell.code_cell.rendered.selected').find('div.input').toggle();
    }


</script>

<a href="javascript:code_toggle_7120154357069289297()">Toggle show/hide</a>




# WaveLab: Storm-Tide and Wave Statisitcs Processing Toolbox

#### Documentation Pages

- <a href="https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/gui.md">Using WaveLab</a>
- <a href="https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/output.md">Output Files<a/>
- <a href="https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/terms.md">Useful Terms</a>
- <a href="https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/storm-tide.md">Storm-Tide Water Level</a>
- <a href="https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/wave-stats.md">Wave Statistics</a>

Feel free to email gpetrochenkov@usgs.gov with any questions.
