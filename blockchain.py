import block

class Blockchain():
    def __init__(self):
        # initialize the list of blocks
        self.list_of_blocks = []

    def add_block(self, bl: block.Block):
        self.list_of_blocks.append(bl)