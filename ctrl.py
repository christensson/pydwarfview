from gi.repository import Gtk, Gdk
import logging
import subprocess

import config
import cmd
import data
import ui

class Controller:
    def __init__(self, args):
        self.log = logging.getLogger('root')
        self.args = args
        self.cfg = config.DwarfConfig(self.args.config_file)
        self.data = data.Data(args.file)
        self.view = ui.Ui(self.cfg)
        self.view.add_exit_handler(self._on_exit_handler)        
        pass

    def main(self):
        Gdk.threads_init()
        self.data.read(self.view)
        self.view.show()
        Gtk.main()
        pass

    def _on_exit_handler(self):
        Gtk.main_quit()
        pass

