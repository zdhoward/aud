from __future__ import annotations

from aud.core.models import AudioFile
from aud.core.selection.policy import SelectionPolicy


class CompositePolicy(SelectionPolicy):
    def __init__(self, *policies: SelectionPolicy):
        self.policies = list(policies)

    def include(self, file: AudioFile) -> bool:
        return all(policy.include(file) for policy in self.policies)
