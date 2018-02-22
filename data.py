import logging
import elftools

from elftools.common.py3compat import bytes2str
from elftools.elf.elffile import ELFFile

class Symbol(object):
    SYMBOL_STRUCT = 1
    SYMBOL_UNION = 2
    SYMBOL_ATTR = 3

    def __init__(self, type, name, props, childs=[]):
        self._type = type
        self._name = name
        self._props = props
        self._childs = childs
        pass

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def properties(self):
        return self._props

    def get_property(self, key):
        if key in self._props:
            return self._props[key]
        else:
            return None

    @property
    def childs(self):
        return self._childs

    @property
    def has_children(self):
        if len(self._childs) > 0:
            return True
        else:
            return False

    def add_child(self, child):
        self._childs.append(child)

    def __repr__(self):
        s = 'Symbol %s, type=%s, has_chidren=%s\n' % (
            self.name, str(self.type), str(self.has_children))
        for attrname, attrval in die.properties.items():
            s += '    |%-18s:  %s\n' % (attrname, attrval)
            pass
        s += 'Children:\n'
        for child in die.childs:
            s += '    |%s\n' % (str(child))
            pass
        return s

class DwarfSymbol(Symbol):
    @staticmethod
    def new_from_die(die):
        symbol = None
        props = []
        if 'DW_TAG_structure_type' == die.tag:
            props['name'] = die.attributes['DW_AT_name'].value.decode()
            props['size'] = die.attributes['DW_AT_byte_size'].value
            childs = []
            if die.has_children:
                for child in die.iter_children():
                    childs.append(DwarfSymbol.new_from_die(child))
                    pass
                pass
            symbol = DwarfSymbol(Symbol.SYMBOL_STRUCT, props['name'], props, childs)
            pass
        elif 'DW_TAG_member' == die.tag:
            props['name'] = die.attributes['DW_AT_name'].value.decode()
            props['type'] = die.attributes['DW_AT_type'].value
            symbol = DwarfSymbol(Symbol.SYMBOL_ATTR, props['name'], props, childs)
            pass
        else:
            pass
        return symbol

    def __init__(self, type, name, props, childs=[]):
        super(DwarfSymbol, self).__init__(type, name, props, childs)
        pass


class Data(object):
    def __init__(self, file):
        self.file = file
        self.log = logging.getLogger('root')
        self.symbols = []
        pass

    def die_repr(self, die):
        s = 'DIE %s, size=%s, has_chidren=%s\n' % (
            die.tag, die.size, die.has_children)
        for attrname, attrval in die.attributes.items():
            s += '    |%-18s:  %s\n' % (attrname, attrval)
        return s

    def read(self, view):
        self.log.info('Reading file %s', self.file)
        with open(self.file, "rb") as f:
            elffile = ELFFile(f)
            if not elffile.has_dwarf_info():
                print('  file has no DWARF info')
                return

            # get_dwarf_info returns a DWARFInfo context object, which is the
            # starting point for all DWARF-based processing in pyelftools.
            dwarfinfo = elffile.get_dwarf_info()

            for CU in dwarfinfo.iter_CUs():
                #self.symbols.append(DwarfSymbol.new_from_die(CU.get_top_DIE()))

                # DWARFInfo allows to iterate over the compile units contained in
                # the .debug_info section. CU is a CompileUnit object, with some
                # computed attributes (such as its offset in the section) and
                # a header which conforms to the DWARF standard. The access to
                # header elements is, as usual, via item-lookup.
                print('  Found a compile unit at offset %s, length %s' % (
                    CU.cu_offset, CU['unit_length']))

                # structs = [die for die in CU.iter_DIEs() if die.tag=='DW_TAG_structure_type']
                for die in CU.iter_DIEs():
                    #print('DIE %s' % (self.die_repr(die)))
                    if 'DW_TAG_structure_type' == die.tag:
                        if 'DW_AT_name' in die.attributes:
                            name = die.attributes['DW_AT_name'].value.decode()
                        else:
                            name = "{}:{}".format(
                                die.attributes['DW_AT_decl_file'].value,
                                die.attributes['DW_AT_decl_line'].value
                            )
                        if 'DW_AT_byte_size' not in die.attributes:
                            continue
                        size = die.attributes['DW_AT_byte_size'].value
                        members = []
                        if die.has_children:
                            for child in die.iter_children():
                                if 'DW_TAG_member' == child.tag:
                                    members.append(child.attributes['DW_AT_name'].value.decode())
                                    pass
                                pass
                            pass
                        view.add(name, "Struct", size, members)
                        pass
                    pass
                pass
            #for s in self.symbols:
            #    print('Sym: %s' % str(s))
            #    pass
            pass
