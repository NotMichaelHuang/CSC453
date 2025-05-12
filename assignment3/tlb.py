class TLB:
    def __init__(self, size):
        self.tlb = []
        self.size = size

    # Virtual page number
    # Physical frame number
    def lookup(self, page):
        for (p, f) in self.tlb:
            if p == page:
                return f
        return None

    def add(self, page, frame): 
        if len(self.tlb) >= self.size:
            self.tlb.pop(0)
        self.tlb.append((page, frame)) 
    
    def get_page_offset(self, address, page_size):
        return ((address // page_size), address % page_size)


