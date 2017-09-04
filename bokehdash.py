import pandas as pd # Import your pet panda
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.models.widgets import Slider, Select, TextInput
from bokeh.layouts import layout, widgetbox
from bokeh.io import curdoc

desc = Div(text=open("description.html").read(), width=800)

wines = pd.read_excel("Teste.xlsx")
output_file("scatter.html")

# Create Input controls
reviews = Slider(title="Minimum number of reviews", value=80, start=0, end=3000, step=10)

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=wines.Price, y=wines.Rating, name=wines.Name, link=wines.Link))

hover = HoverTool(tooltips=[
    ("Name", "@name"),
    ("Rating", "@rating"),
    ("Price", "@price"),
    ("Link", "@link")
])

p = figure(plot_height=600, plot_width=700, title="Vivino offerings", toolbar_location=None, tools=[hover])
p.circle('x', 'y', size=20, source=source)


def select_wines():
    selected = wines[(wines.Reviews >= reviews.value)]
    return selected

def update():
    wines = select_wines()
    p.title.text = "%d wines selected" % len(wines)
    source.data = data=dict(x=wines.Price, y=wines.Rating, name=wines.Name, link=wines.Link)

controls = [reviews]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()

curdoc().add_root(l)
curdoc().title = "Wines"

show(p)

