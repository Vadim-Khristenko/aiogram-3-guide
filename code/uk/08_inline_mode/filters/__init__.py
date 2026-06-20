from .text_has_link import HasLinkFilter
from .check_via_bot import ViaBotFilter

# Робимо так, щоб потім просто імпортувати
# from filters import HasLinkFilter
__all__ = [
    "HasLinkFilter",
    "ViaBotFilter"
]
