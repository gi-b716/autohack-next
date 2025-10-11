# __version_type__ = "release"

__version_type__ = "dev"

# __version_type__ = "post"

__version__ = "1.1.0"

# --------------------------------------------

import time

timeInfo = time.strftime("%Y%m%d", time.localtime())

__version__ = f"{__version__}{"" if __version_type__ == 'release' else f".{__version_type__}{timeInfo}"}"

__app_version__ = __version__
