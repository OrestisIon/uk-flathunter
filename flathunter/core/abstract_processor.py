"""Abstract class defining the 'Processor' interface"""
from typing import Dict, Union

# Import domain model - but keep as optional for backward compatibility
try:
    from flathunter.domain.models import Expose
    ExposeType = Union[Dict, Expose]
except ImportError:
    ExposeType = Dict

class Processor:
    """Processor interface. Flathunter runs sequences of exposes through
       a set of processors that stack on each other"""

    def process_expose(self, expose: ExposeType) -> ExposeType:
        """Mutate the expose. Should be implemented in the subclass"""
        return expose

    def process_exposes(self, exposes):
        """Apply the processor to every expose in the sequence"""
        return map(self.process_expose, exposes)
