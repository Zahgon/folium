from branca.element import Figure, MacroElement

from folium.elements import EventHandler, JSCSSMixin
from folium.folium import Map
from folium.map import LayerControl
from folium.template import Template
from folium.utilities import JsCode, deep_copy


class DualMap(JSCSSMixin, MacroElement):
    """Create two maps in the same window.

    Adding children to this objects adds them to both maps. You can access
    the individual maps with `DualMap.m1` and `DualMap.m2`.

    Uses the Leaflet plugin Sync: https://github.com/jieter/Leaflet.Sync

    Parameters
    ----------
    location: tuple or list, optional
        Latitude and longitude of center point of the maps.
    layout : {'horizontal', 'vertical'}
        Select how the two maps should be positioned. Either horizontal (left
        and right) or vertical (top and bottom).
    **kwargs
        Keyword arguments are passed to the two Map objects.

    Examples
    --------
    >>> # DualMap accepts the same arguments as Map:
    >>> m = DualMap(location=(0, 0), tiles="cartodbpositron", zoom_start=5)
    >>> # Add the same marker to both maps:
    >>> Marker((0, 0)).add_to(m)
    >>> # The individual maps are attributes called `m1` and `m2`:
    >>> Marker((0, 1)).add_to(m.m1)
    >>> LayerControl().add_to(m)
    >>> m.save("map.html")

    """

    _template = Template("""
        {% macro script(this, kwargs) %}
            {{ this.m1.get_name() }}.sync({{ this.m2.get_name() }});
            {{ this.m2.get_name() }}.sync({{ this.m1.get_name() }});
        {% endmacro %}
    """)

    default_js = [
        (
            "Leaflet.Sync",
            "https://cdn.jsdelivr.net/gh/jieter/Leaflet.Sync/L.Map.Sync.min.js",
        )
    ]

    def __init__(self, location=None, layout="horizontal", **kwargs):
        super().__init__()
        for key in ("width", "height", "left", "top", "position"):
            assert key not in kwargs, f"Argument {key} cannot be used with  DualMap."
        if layout not in ("horizontal", "vertical"):
            raise ValueError(
                f"Undefined option for argument `layout`: {layout}. "
                "Use either 'horizontal' or 'vertical'."
            )
        width = "50%" if layout == "horizontal" else "100%"
        height = "100%" if layout == "horizontal" else "50%"
        self.m1 = Map(
            location=location,
            width=width,
            height=height,
            left="0%",
            top="0%",
            position="absolute",
            **kwargs,
        )
        self.m2 = Map(
            location=location,
            width=width,
            height=height,
            left="50%" if layout == "horizontal" else "0%",
            top="0%" if layout == "horizontal" else "50%",
            position="absolute",
            **kwargs,
        )
        figure = Figure()
        figure.add_child(self.m1)
        figure.add_child(self.m2)
        # Important: add self to Figure last.
        figure.add_child(self)
        self.children_for_m2 = []
        self.children_for_m2_copied = []  # list with ids

    def _repr_html_(self, **kwargs):
        """Displays the HTML Map in a Jupyter notebook."""
        pass

    def add_child(self, child, name=None, index=None):
        """Add object `child` to the first map and store it for the second."""
        self.m1.add_child(child, name, index)
        if index is None:
            index = len(self.m2._children)
        self.children_for_m2.append((child, name, index))

    def on(self, **event_map: JsCode):
        """Add event handlers to both maps at once"""
        self._add(once=False, **event_map)

    def once(self, **event_map: JsCode):
        """Add event handlers to both maps at once"""
        pass

    def _add(self, once: bool, **event_map: JsCode):
        for event_type, handler in event_map.items():
            self.m1.add_child(EventHandler(event_type, handler, once))
            self.m2.add_child(EventHandler(event_type, handler, once))

    def render(self, **kwargs):
        pass

    def fit_bounds(self, *args, **kwargs):
        pass

    def keep_in_front(self, *args):
        pass
