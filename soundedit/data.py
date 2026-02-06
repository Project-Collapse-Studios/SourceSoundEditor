"""Represents all underlaying sound operators data, in a KeyValue format."""
from pathlib import Path
from srctools import Keyvalues


class NodeData:
    def __init__(self):
        self.file_path = None # Stores the file location for the "Save" function.
        self.kvdata = Keyvalues.root(
            Keyvalues("start_stacks", []),
            Keyvalues("update_stacks", []),
            Keyvalues("stop_stacks", [])
        )

    def LoadSndOperatorStacks(self, file: str|Path):
        """Loads sound_operator_stacks.txt"""
        self.file_path = Path(file)

        if not self.file_path.is_file():
            raise FileNotFoundError(f"File {file} does not exist!")
        
        with open(file) as f:
            self.kvdata = Keyvalues.parse(f.read())

        print("File parsed!")


    def GetStartStacks(self) -> Keyvalues:
        """Shortcut method, get the start stacks."""
        return self.kvdata.find_block("start_stacks", or_blank=True)
    
    def GetUpdateStacks(self) -> Keyvalues:
        """Shortcut method, get the update stacks."""
        return self.kvdata.find_block("update_stacks", or_blank=True)
    
    def GetStopStacks(self) -> Keyvalues:
        """Shortcut method, get the stop stacks."""
        return self.kvdata.find_block("stop_stacks", or_blank=True)


