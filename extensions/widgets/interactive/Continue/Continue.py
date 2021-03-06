from core.domain import widget_domain
from extensions.value_generators.models import generators


class Continue(widget_domain.BaseWidget):
    """Definition of a widget.

    Do NOT make any changes to this widget definition while the Oppia app is
    running, otherwise things will break.

    This class represents a widget, whose id is the name of the class. It is
    auto-discovered when the default widgets are refreshed.
    """

    # The human-readable name of the widget.
    name = 'Continue (Default widget)'

    # The category the widget falls under in the widget repository.
    category = 'Basic Input'

    # A description of the widget.
    description = ('A button allowing the user to continue to the next section '
                   'of the exploration.')

    # Customization parameters and their descriptions, types and default
    # values. This attribute name MUST be prefixed by '_'.
    _params = [{
        'name': 'buttonText',
        'description': 'The text that should be displayed on the button.',
        'generator': generators.Copier,
        'init_args': {},
        'customization_args': {
            'value': 'Continue'
        },
        'obj_type': 'UnicodeString'
    }]

    # Actions that the reader can perform on this widget which trigger a
    # feedback interaction, and the associated input types. Interactive widgets
    # must have at least one of these. This attribute name MUST be prefixed by
    # '_'.
    _handlers = [{
        'name': 'submit', 'input_type': None
    }]
