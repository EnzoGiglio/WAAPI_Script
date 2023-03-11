import configparser
import io
import os
import re

from dataclasses import dataclass


@dataclass
class ImportTemplate:
    name: str = None

    def is_valid(self) -> bool:
        return self.name is not None

    @staticmethod
    def from_notes(notes: str):
        # disable inspection because we just want to return
        # default invalid data class on any error and not care about it downstream
        # noinspection PyBroadException
        try:
            parser = configparser.ConfigParser()
            parser.read_string(notes)
            return ImportTemplate(
                parser['Import_Template']['Name']
            )
        except Exception:
            return ImportTemplate()


@dataclass
class ImportSlot:
    name: str = None

    def is_valid(self) -> bool:
        return self.name is not None

    @staticmethod
    def from_notes(notes: str):
        # noinspection PyBroadException
        try:
            parser = configparser.ConfigParser()
            parser.read_string(notes)
            return ImportTemplate(
                parser['Import_Slot']['Name']
            )
        except Exception:
            return ImportSlot()


_wav_name_re = re.compile('\[(\w+)\]\s+(\w+)\s+\((\w+)\)\s+(\d+)\.wav')


@dataclass
class ImportedHierarchy:
    template_id: str = None

    def is_valid(self) -> bool:
        return self.template_id is not None

    def to_notes(self) -> str:
        cfg = configparser.ConfigParser()
        cfg['Imported_Hierarchy'] = {
            'Template_ID': self.template_id
        }
        sb = io.StringIO()
        cfg.write(sb)
        return sb.getvalue()

    @staticmethod
    def from_notes(notes: str):
        # noinspection PyBroadException
        try:
            parser = configparser.ConfigParser()
            parser.read_string(notes)
            return ImportTemplate(
                parser['Imported_Hierarchy']['Template_ID']
            )
        except Exception:
            return ImportedHierarchy()


@dataclass
class ImportedWav:
    template_name: str = None
    obj_name: str = None
    slot_name: str = None
    variation: int = None

    def is_valid(self) -> bool:
        return (
                self.template_name is not None and
                self.slot_name is not None and
                self.variation is not None
        )

    @staticmethod
    def from_filename(file_name: str):
        if not os.path.exists(file_name):
            return ImportedWav()
        # noinspection PyBroadException
        try:
            name = os.path.basename(file_name)
            m = re.match(_wav_name_re, name)
            if m:
                return ImportedWav(m[1], m[2], m[3], m[4])
            else:
                return ImportedWav()
        except Exception:
            return ImportedWav()
