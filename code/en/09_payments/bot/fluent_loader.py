from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader


def get_fluent_localization() -> FluentLocalization:
    """
    Loading 'locale.ftl' file with locales from the 'l10n' directory in the current location
    :return: FluentLocalization object
    """

    # Checks to ensure
    # the presence of the correct file in the correct directory
    locale_dir = Path(__file__).parent.joinpath("l10n")
    if not locale_dir.exists():
        error = "'l10n' directory not found"
        raise FileNotFoundError(error)
    if not locale_dir.is_dir():
        error = "'l10n' is not a directory"
        raise NotADirectoryError(error)
    locale_file = Path(locale_dir, "locale.ftl")
    if not locale_file.exists():
        error = "locale.txt file not found"
        raise FileNotFoundError(error)

    # Create necessary objects and return FluentLocalization object
    l10n_loader = FluentResourceLoader(
        str(locale_file.absolute()),
    )
    return FluentLocalization(
        locales=["en"],
        resource_ids=[str(locale_file.absolute())],
        resource_loader=l10n_loader
    )
