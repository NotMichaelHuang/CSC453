class PageTable:
    def __init__ (self):
        self.valid = False 
        self.frame = -1

class PageTableEntry:
    def __init__(self, num_pages):
        self.entries = [PageTable() for _ in range(num_pages)]
    
    def is_valid(self, page):
        return self.entries[page].valid
    
    def get_frame(self, page):
        return self.entries[page].frame

    def set_frame(self, page, frame):
        entry = self.entries[page]
        entry.valid = True
        entry.frame = frame
    
    def remove_frame(self, page):
        entry = self.entries[page]
        entry.valid = False
        entry.frame = -1
    
    # Debugging
    # def get_table(self):
    #   return self.entries


