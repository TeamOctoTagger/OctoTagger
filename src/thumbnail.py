import database
import itemview

import mimetypes
import os
import types
import hashlib

DEFAULT_ICON = "./icons/generic.png"

GENERIC = {
    "folder": "./icons/folder.png",
}

_map = {}

# TODO: Error handling when loading thumbnails


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


def get_thumbnail(item, path_only=False):

    is_db_item = True

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
        is_db_item = False
    else:
        raise TypeError("Unknown item type", item)

    # FIXME mimetypes uses file extension, switch to libmagic
    if is_db_item:
        file_type, file_encoding = mimetypes.guess_type(row[0])
    else:
        file_type, file_encoding = mimetypes.guess_type(
            os.path.basename(item)
        )

    if file_type not in _map:
        # no icon specified
        return DEFAULT_ICON

    handler = _map[file_type]

    if type(handler) is str:
        return handler
    elif isinstance(handler, types.FunctionType):

        if is_db_item:
            thumbnail_path = os.path.join(
                database.get_current_gallery("directory"),
                "thumbnails",
                row[1],
            )
            if not os.path.isfile(thumbnail_path):
                try:
                    handler(path, thumbnail_path)
                except:
                    return DEFAULT_ICON
            if not path_only:
                return thumbnail_path
            else:
                return None
        else:
            # Generate unique name
            md5 = hashlib.md5()
            md5.update(item)
            thumbnail_name = md5.hexdigest()

            thumbnail_path = os.path.join(
                database.get_current_gallery("directory"),
                "thumbnails",
                "temp",
                thumbnail_name
            )
            handler(path, thumbnail_path)
            return thumbnail_path


def _handler_pil(source, destination):
    from PIL import Image
    # FIXME: "struct.error: unpack requires a string argument of length 4"
    # with some images.
    image = Image.open(source).convert()
    image.thumbnail(itemview.THUMBNAIL_SIZE)
    image.save(destination, "PNG")


register("image/jpeg", _handler_pil)
register("image/png", _handler_pil)
