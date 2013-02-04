from gi.repository import Gtk, Gdk
import threading
import logging
import collections

import os
import datetime

class Ui:
    (SYM_LIST_NAME,
     SYM_LIST_TYPE,
     SYM_LIST_SIZE,
     THUMB_LIST_NUM_COLS) = range(4)

    UI_FILE = 'ui.glade'

    def __init__(self, cfg):
        self.cfg = cfg
        self.log = logging.getLogger('root')

        # Data
        self.on_exit_handler = None

        self._createUi()
        pass

    def _createUi(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.UI_FILE)

        self.main_window = self.builder.get_object('main_window')

        # Folder navigation tree
        self.sym_store = Gtk.TreeStore(str, str, int)

        sym_tree = self.builder.get_object('symbol_treeview')
        sym_tree.set_model(self.sym_store)
        sym_tree.set_search_column(self.SYM_LIST_NAME)
        sym_tree_renderer = Gtk.CellRendererText()
        
        sym_tree_name_col = Gtk.TreeViewColumn(
                                               "Name", sym_tree_renderer, text=self.SYM_LIST_NAME)
        sym_tree_type_col = Gtk.TreeViewColumn(
                                               "Type", sym_tree_renderer, text=self.SYM_LIST_TYPE)
        sym_tree_size_col = Gtk.TreeViewColumn(
                                               "Size", sym_tree_renderer, text=self.SYM_LIST_SIZE)

        sym_tree_name_col.set_resizable(True)
        sym_tree_type_col.set_resizable(True)
        sym_tree_size_col.set_resizable(True)
    
        sym_tree.append_column(sym_tree_name_col)
        sym_tree.append_column(sym_tree_type_col)
        sym_tree.append_column(sym_tree_size_col)

        handlers = {
                    'on_main_window_destroy' : self._exit_handler,
                    }
        self.builder.connect_signals(handlers)
        pass

    def _exit_handler(self, widget):
        self.log.info("User exit requested!")
        if self.on_exit_handler is not None:
            self.on_exit_handler()
            pass
        else:
            self.log.warning("No exit handler installed!")
            pass
        pass

    def add_exit_handler(self, on_exit_handler):
        self.on_exit_handler = on_exit_handler
        pass

    def add(self, name, type_name, size, members):
        tree_iter = self.sym_store.append(None, [name, type_name, size])
        for member in members:
            self.sym_store.append(tree_iter, [member, "member", 0])
            pass
        pass

    def show(self):
        self.main_window.show_all()
        pass
