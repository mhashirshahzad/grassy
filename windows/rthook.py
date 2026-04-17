import os
import sys

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS

    # core binary search path
    os.environ['PATH'] = base_dir + os.pathsep + os.environ.get('PATH', '')

    # GI bindings (CRITICAL for GTK)
    os.environ['GI_TYPELIB_PATH'] = os.path.join(base_dir, 'lib', 'girepository-1.0')

    # pixbuf loaders
    os.environ['GDK_PIXBUF_MODULE_FILE'] = os.path.join(
        base_dir, 'lib', 'gdk-pixbuf-2.0', 'loaders.cache'
    )

    # shared data (themes, schemas)
    os.environ['XDG_DATA_DIRS'] = base_dir + os.pathsep + os.environ.get('XDG_DATA_DIRS', '')
