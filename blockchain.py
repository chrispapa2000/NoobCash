import block

class Blockchain():
    def __init__(self, block_capacity=5):
        # initialize the list of blocks
        self.list_of_blocks = []
        self.block_capacity = block_capacity

    def add_block(self, bl: block.Block):
        self.list_of_blocks.append(bl.to_dict())

    def get_block_capacity(self):
        return self.block_capacity
