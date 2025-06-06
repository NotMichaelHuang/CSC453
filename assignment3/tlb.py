from collections import deque

class TLB:
    def __init__(self, size=16):
        # FIFO queue that automatically drops the oldest entry when full
        self.entries = deque(maxlen=size)

    def lookup(self, page):
        for p, f in self.entries:
            if p == page:
                return f
        return None

    def add(self, page, frame):
        # Only insert if it’s not already cached
        if not any(p == page for p, _ in self.entries):
            # If entries is full, this append auto‐pops the oldest
            self.entries.append((page, frame))

    def get_page_offset(self, addr, page_size):
        return ((addr // page_size), (addr % page_size))

    def invalidate(self, page_to_remove):
        """
        Remove any entry whose page == page_to_remove.
        This is called when that page has been evicted from RAM.
        """
        # Filter out the victim page, rebuild the deque with same maxlen
        self.entries = deque([(p, f) for (p, f) in self.entries if p != page_to_remove], maxlen=self.entries.maxlen)
