from .text_has_link import HasLinkFilter
from .check_via_bot import ViaBotFilter

# Make it so that we can then simply import
# from filters import HasLinkFilter
__all__ = [
    "HasLinkFilter",
    "ViaBotFilter"
]
