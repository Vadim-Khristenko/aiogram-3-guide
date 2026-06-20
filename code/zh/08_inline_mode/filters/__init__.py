from .text_has_link import HasLinkFilter
from .check_via_bot import ViaBotFilter

# 这样我们就可以直接导入
# from filters import HasLinkFilter
__all__ = [
    "HasLinkFilter",
    "ViaBotFilter"
]
