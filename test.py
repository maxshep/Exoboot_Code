from dataclasses import dataclass, field, InitVar
from typing import List


@dataclass
class Book:
    '''Object for tracking physical books in a collection.'''
    name: str
    do_include_FSRs: InitVar[bool] = False
    weight: float = field(default=0.0, repr=False)
    shelf_id: int = field(init=False)
    chapters: List[str] = field(default_factory=list)
    condition: str = field(default="Good", compare=False)

    def __post_init__(self, do_include_FSRs):
        if do_include_FSRs:
            self.shelf_id = None
        else:
            self.shelf_id = 0


book = Book(name='hi', do_include_FSRs=True)
print(book.shelf_id)
print(book)
