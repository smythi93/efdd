import os
from typing import Optional, Dict, Tuple, List

from sflkit.config import hash_identifier
from sflkit.events.mapping import EventMapping
from sflkitlib.events import EventType
from sflkitlib.events.event import (
    Event,
    LineEvent,
    BranchEvent,
    FunctionEnterEvent,
    FunctionExitEvent,
    FunctionErrorEvent,
    DefEvent,
    UseEvent,
    ConditionEvent,
    LoopBeginEvent,
    LoopEndEvent,
    LoopHitEvent,
    LenEvent,
)


def identifier(target_path: os.PathLike):
    return hash_identifier(target_path)


class Mapping:
    def __init__(self, mapping: dict[Event, Optional[Event]] = None):
        self.mapping = mapping or dict()


class MappingCreator:
    def __init__(self, origin: EventMapping):
        self.origin = origin
        self.location_map: Dict[str, Dict[int, Dict[EventType, List[Event]]]] = dict()
        self.rebuild()

    def rebuild(self):
        for event_id in self.origin:
            event = self.origin.get(event_id)
            if event:
                file = event.file
                if file not in self.location_map:
                    self.location_map[file] = dict()
                line = event.line
                if line not in self.location_map[file]:
                    self.location_map[file][line] = dict()
                event_type = event.event_type
                if event_type not in self.location_map[file][line]:
                    self.location_map[file][line][event_type] = list()
                self.location_map[file][line][event_type].append(event)

    def get_possible_events(
        self, event: Event, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ) -> List[Event]:
        file = event.file
        line = event.line
        if (file, line) in patch:
            file, line = patch[(file, line)]
        event_type = event.event_type
        if file in self.location_map:
            if line in self.location_map[file]:
                if event_type in self.location_map[file][line]:
                    return self.location_map[file][line][event_type]
        return None

    def map_generic(
        self, event: Event, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ) -> Optional[Event]:
        events = self.get_possible_events(event, patch)
        if events:
            return events[0]
        else:
            return None

    def map_line(self, event: LineEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]):
        return self.map_generic(event, patch)

    def map_branch(
        self, event: BranchEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        events = self.get_possible_events(event, patch)
        if events:
            for candidate in events:
                candidate: BranchEvent
                if event.then_id > event.else_id:
                    if candidate.then_id > candidate.else_id:
                        return candidate
                elif event.then_id < event.else_id:
                    if candidate.then_id < candidate.else_id:
                        return candidate
        else:
            return None

    def map_function_enter(
        self, event: FunctionEnterEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        return self.map_generic(event, patch)

    def map_function_error(
        self, event: FunctionErrorEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        return self.map_generic(event, patch)

    def map_function_exit(
        self, event: FunctionExitEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        return self.map_generic(event, patch)

    def map_def(self, event: DefEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]):
        events = self.get_possible_events(event, patch)
        if events:
            for candidate in events:
                candidate: DefEvent
                if event.var == candidate.var:
                    return candidate
        else:
            return None

    def map_use(self, event: UseEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]):
        events = self.get_possible_events(event, patch)
        if events:
            for candidate in events:
                candidate: UseEvent
                if event.var == candidate.var:
                    return candidate
        else:
            return None

    def map_condition(
        self, event: ConditionEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        events = self.get_possible_events(event, patch)
        if events:
            for candidate in events:
                candidate: ConditionEvent
                if event.condition == candidate.condition:
                    return candidate
        else:
            return None

    def map_loop_begin(
        self, event: LoopBeginEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        return self.map_generic(event, patch)

    def map_loop_hit(
        self, event: LoopHitEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        return self.map_generic(event, patch)

    def map_loop_end(
        self, event: LoopEndEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        return self.map_generic(event, patch)

    def map_len_event(
        self, event: LenEvent, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ):
        events = self.get_possible_events(event, patch)
        if events:
            for candidate in events:
                candidate: LenEvent
                if event.var == candidate.var:
                    return candidate
        else:
            return None

    def create(
        self, target: EventMapping, patch: Dict[Tuple[str, int], Tuple[str, int]]
    ) -> Mapping:
        mapping = dict()
        for event_id in target:
            event = target.get(event_id)
            if event:
                match event.event_type:
                    case EventType.LINE:
                        mapped = self.map_line(event, patch)
                    case EventType.BRANCH:
                        mapped = self.map_branch(event, patch)
                    case EventType.FUNCTION_ENTER:
                        mapped = self.map_function_enter(event, patch)
                    case EventType.FUNCTION_EXIT:
                        mapped = self.map_function_exit(event, patch)
                    case EventType.FUNCTION_ERROR:
                        mapped = self.map_function_error(event, patch)
                    case EventType.DEF:
                        mapped = self.map_def(event, patch)
                    case EventType.USE:
                        mapped = self.map_use(event, patch)
                    case EventType.CONDITION:
                        mapped = self.map_condition(event, patch)
                    case EventType.LOOP_BEGIN:
                        mapped = self.map_loop_begin(event, patch)
                    case EventType.LOOP_HIT:
                        mapped = self.map_loop_hit(event, patch)
                    case EventType.LOOP_END:
                        mapped = self.map_loop_end(event, patch)
                    case EventType.LEN:
                        mapped = self.map_len_event(event, patch)
                    case _:
                        mapped = None
                if mapped:
                    mapping[event] = mapped
        return Mapping(mapping)
