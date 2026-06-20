from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader


def get_fluent_localization() -> FluentLocalization:
    """
    从当前位置的 'l10n' 目录加载 'locale.ftl' 文件中的区域设置
    :return: FluentLocalization 对象
    """

    # 检查以确保
    # 正确的文件存在于正确的目录中
    locale_dir = Path(__file__).parent.joinpath("l10n")
    if not locale_dir.exists():
        error = "'l10n' 目录未找到"
        raise FileNotFoundError(error)
    if not locale_dir.is_dir():
        error = "'l10n' 不是目录"
        raise NotADirectoryError(error)
    locale_file = Path(locale_dir, "locale.ftl")
    if not locale_file.exists():
        error = "locale.txt 文件未找到"
        raise FileNotFoundError(error)

    # 创建必要的对象并返回 FluentLocalization 对象
    l10n_loader = FluentResourceLoader(
        str(locale_file.absolute()),
    )
    return FluentLocalization(
        locales=["en"],
        resource_ids=[str(locale_file.absolute())],
        resource_loader=l10n_loader
    )
