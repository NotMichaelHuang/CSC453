import bisect
from abc import ABC, abstractmethod
from collections import deque


# Cannot initialize this class
class ReplacementPolicies(ABC):
    """
    Abstract base-page 
    """

    @abstractmethod
    def add(self, page: int) -> None:
        """
        Add new page 
        """
        pass

    @abstractmethod
    def access(self, page: int, time: int) ->  None:
        """
        Call on every memory access
        time: track which one was last used, LRU purposes
        """
        pass

    @abstractmethod
    def evict(self, current_time: int) -> int:
        """
        Change and return the victim page
        current_time: index of the current reference, OPT purposes
        """
        pass

    @abstractmethod
    def remove(self, page: int) -> None:
        """
        remove the victim page from the internal tracking
        """
        pass


class FIFOReplacement(ReplacementPolicies):
    def __init__(self):
        self.queue = deque()

    def add(self, page):
        self.queue.append(page) 
    
    # Just to keep it consistent with LRU and OPT
    def access(self, page, time):
        pass
    
    def evict(self, current_time):
        return self.queue.popleft() # remove/return
    
    def remove(self, page):
        pass


class LRUReplacement(ReplacementPolicies):
    def __init__(self):
        self.last_used = {}
        self.pages = set()

    def access(self, page, time):
        # Update the time step for this page to prevent incorrect eviction
        self.last_used[page] = time
    
    def add(self, page):
        self.pages.add(page)

    def evict(self, current_time):
        # iterate through self.pages and find the smallest time step recorded or return -1
        return min(self.pages, key=lambda p: self.last_used.get(p, -1))

    def remove(self, page):
        self.pages.remove(page)
        self.last_used.pop(page, None) # None is to prevent KeyError

class OPTReplacement:
    def __init__(self, future_indices: dict[int, list[int]]):
        """
        future_indices: 
          page_num → sorted list of upcoming reference indices for that page
        """
        self.future = future_indices
        self.pages = set()  # pages currently resident in RAM

    def add(self, page: int) -> None:
        """Call this when you load a new page into a frame."""
        self.pages.add(page)

    def access(self, page: int, time: int) -> None:
        """
        OPT doesn’t need per-access tracking, so this is a no-op.
        We keep it here so all policies share the same interface.
        """
        pass

    def evict(self, current_time: int) -> int:
        """
        Return the page whose *next* use is farthest in the future,
        or one that’s never used again.
        """
        victim = None
        farthest_next = -1

        for p in self.pages:
            uses = self.future.get(p, [])
            # find the first future index > current_time
            i = bisect.bisect_right(uses, current_time)
            if i >= len(uses):
                # no more future uses → ideal victim
                return p
            # otherwise compare how far away its next use is
            if uses[i] > farthest_next:
                farthest_next = uses[i]
                victim = p

        return victim

    def remove(self, page: int) -> None:
        """Call this after you evict a page to clean up state."""
        self.pages.remove(page)

