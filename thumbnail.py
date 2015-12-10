import database
import itemview

import mimetypes
import os
import types

DEFAULT_ICON = "./icons/generic.png"

GENERIC = {
    "folder": "./icons/folder.png",
}

_map = {}


def register(mime_type, handler):
    if mime_type in _map:
        raise KeyError("Handler for this type already exists", mime_type)

    if type(handler) is str and not os.path.isfile(handler):
        # static icon
        raise ValueError("Expected path to file", handler)
    elif isinstance(handler, types.FunctionType):
        # generate thumbnail
        pass
    else:
        raise TypeError("Unknown handler type", type(handler))

    _map[mime_type] = handler


def get_thumbnail(item):
    if type(item) is int:  # item is db id
        connection = database.get_current_gallery("connection").cursor()
        connection.execute(
            (
                'SELECT file_name, uuid '
                'FROM file '
                'WHERE file.pk_id=:id '
            ),
            {
                'id': item,
            }
        )
        row = connection.fetchone()
        if row is None:
            raise ValueError('Item not found in database', item)

        path = os.path.join(
            database.get_current_gallery("directory"),
            "files",
            row[1],
        )
    elif type(item) is str:  # item is fs path
        path = item
    else:
        raise TypeError("Unknown item type", item)

    # FIXME mimetypes uses file extension, switch to libmagic
    file_type, file_encoding = mimetypes.guess_type(row[0])

    if file_type not in _map:
        # no icon specified
        return DEFAULT_ICON

    handler = _map[file_type]

    if type(handler) is str:
        return handler
    elif isinstance(handler, types.FunctionType):
        thumbnail_path = os.path.join(
            database.get_current_gallery("directory"),
            "thumbnails",
            row[1],
        )
        if not os.path.isfile(thumbnail_path):
            handler(path, thumbnail_path)
        return thumbnail_path


def _handler_pil(source, destination):
    from PIL import Image
    image = Image.open(source).convert()
    image.thumbnail(itemview.THUMBNAIL_SIZE)
    image.save(destination, "PNG")


register("image/jpeg", _handler_pil)
register("image/png", _handler_pil)
