from abc import ABC
from datetime import datetime
from shutil import copy
import pathlib
import os
import re



class GameEngineText:
    def __init__(self):
        self._titles = ["Renpy", "RPG Maker MV"]
        self._keys = ["renpy", "rpgmaker_mv"]
        self._title_to_key = {"Renpy": "renpy", "RPG Maker MV": "rpgmaker_mv"}
        self._key_to_title = {"renpy": "Renpy", "rpgmaker_mv": "RPG Maker MV"}
    def get_titles(self):
        return self._titles
    def get_keys(self):
        return self._keys
    def title_to_key(self, title):
        return self._title_to_key[title]
    def key_to_title(self, key):
        return self._key_to_title[key]


class Patcher(ABC):
    def run(self):
        pass

    def set_patch(self):
        pass

    def load_args(self, *kwargs):
        pass


class PatchFuncSkeletion(ABC):
    
    pass

def reg_it(data):
    return re.sub(rb"if\s\(this\.\_skipCount\s={3}\s0\)", b"if (this._skipCount < 0)", data)
    pass
class RPGMakerMVPatchFuncs():
    def _freeze_fix(self, file_path):
        patch_location = "/www/js/"
        
        if not file_path.endswith(".js") and pathlib.Path(file_path).is_file():
            return
        if pathlib.Path(file_path).is_dir():
            file_path = pathlib.Path(file_path+"/"+patch_location+"rpg_core.js")
        

        backup_file(file_path)
        with open(file_path, mode="r") as file_p:
            lines = []
            for line in file_p.readlines():
                if "if (this._skipCount === 0)" in line:
                    line = re.sub(r"if\s\(this\.\_skipCount\s={3}\s0\)", "if (this._skipCount < 0)", line, re.DOTALL)
                lines.append(line)
                


        with open(file_path, mode="w") as file_p:
            for line in lines:
                file_p.writelines(line)
                    
                
                #Z:\Games\Japan\Hentai\TEMP\DESIRE EATER
        pass
    def _debug_mode(self):
        pass
    def _cheat_menu(self):
        pass
    pass

class RenpyPatchFuncs():
    def _unpack_game(self):
        pass
    def _debug_mode(self):
        pass
    def _cheat_menu(self):
        pass
    pass

class PatchSkeleton(ABC):
    def get_keys(self):
        pass
    def get_titles(self):
        pass
    def title_to_key(self, title):
        pass
    def key_to_title(self, key):
        pass
    pass


class RpgmakerMVPatches(PatchSkeleton):
    def __init__(self):
        super().__init__()
        self.patchfunc = RPGMakerMVPatchFuncs()
        self._title_to_key = {
            "Freeze fix": "freeze_fix",
            "Cheat menu": "cheat_menu",
            "Debug mode": "debug_mode"
        }
        self._key_to_title = {
            "freeze_fix": "Freeze fix",
            "cheat_menu": "Cheat menu",
            "debug_mode": "Debug mode"
        }
        self.patches = {
            "freeze_fix": self.patchfunc._freeze_fix,
            "cheat_menu": self.patchfunc._cheat_menu,
            "debug_mode": self.patchfunc._debug_mode
        }
        self.titles = ["Freeze fix", "Cheat menu", "Debug mode"]
        self.keys = ["freeze_fix", "cheat_menu", "debug_mode"]
        self.patch = ""
    def set_patch(self, patch):
        self.patch = self.title_to_key(patch)
    def get_patch(self):
        return self.patches[self.patch]
    def title_to_key(self, title):
        return self._title_to_key[title]
    def key_to_title(self, key):
        return self._key_to_title[key]
    def get_titles(self):
        return self.titles
    def get_keys(self):
        return self.keys

class RenpyPatches(PatchSkeleton):
    def __init__(self):
        super().__init__()
        self.patchfunc = RenpyPatchFuncs()
        self._title_to_key = {
            "Unpack game": "unpack_game",
            "Cheat menu": "cheat_menu",
            "Debug mode": "debug_mode"
        }
        self._key_to_title = {
            "unpack_game": "Unpack game",
            "cheat_menu": "Cheat menu",
            "debug_mode": "Debug mode"
        }
        self.patches = {
            "unpack_game": self.patchfunc._unpack_game,
            "cheat_menu": self.patchfunc._cheat_menu,
            "debug_mode": self.patchfunc._debug_mode
        }
        self.titles = ["Unpack game", "Cheat menu", "Debug mode"]
        self.keys = ["unpack_game", "cheat_menu", "debug_mode"]
        self.patch = ""
    def set_patch(self, patch):
        self.patch = self.title_to_key(patch)
    def get_patch(self):
        return self.patches[patch]
    def title_to_key(self, title):
        return self._title_to_key[title]
    def key_to_title(self, key):
        return self._key_to_title[key]
    def get_titles(self):
        return self.titles
    def get_keys(self):
        return self.keys
        
class GamePatcher:
    def __init__(self, game_engine=None):
        self.game_patch_objects = {
            "renpy": RenpyPatches(),
            "rpgmaker_mv": RpgmakerMVPatches()
        }
        self.engine_text_helper = GameEngineText()
        self.game_patches = None
        if game_engine is not None:
            self.game_engine = self.engine_text_helper.title_to_key(game_engine)
            self.game_patches = self.game_patch_objects[self.game_engine]
        
    def get_keys(self):
        return self.game_patches.get_keys()
    def get_titles(self):
        return self.game_patches.get_titles()
    def title_to_key(self, title):
        return self.game_patches.title_to_key(title)
    def key_to_title(self, key):
        return self.game_patches.key_to_title(key)
    def set_engine(self, game_engine):
        self.game_engine = game_engine
        self.game_patches = self.game_patch_objects[self.game_engine]
    def get_patch(self, patch):
        self.game_patches.set_patch(patch)
        return self.game_patches.get_patch()
        
    pass

def backup_file(filename):
    backup_file = pathlib.Path(filename.parent / (filename.name+" "+str(datetime.now())[:19].replace(":", ".")+".bak"))
    if not pathlib.Path(backup_file).exists():
        copy(filename, backup_file)
    pass
