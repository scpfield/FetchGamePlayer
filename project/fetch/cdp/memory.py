# DO NOT EDIT THIS FILE!
#
# This file is generated from the CDP specification. If you need to make
# changes, edit the generator and regenerate all of the modules.
#
# CDP domain: Memory (experimental)

from __future__ import annotations
import enum
import typing
from dataclasses import dataclass
from .util import event_class, T_JSON_DICT


class PressureLevel(enum.Enum):
    '''
    Memory pressure level.
    '''
    MODERATE = "moderate"
    CRITICAL = "critical"

    def to_json(self) -> str:
        return self.value

    @classmethod
    def from_json(cls, json: str) -> PressureLevel:
        return cls(json)


@dataclass
class SamplingProfileNode:
    '''
    Heap profile sample.
    '''
    #: Size of the sampled allocation.
    size: float

    #: Total bytes attributed to this sample.
    total: float

    #: Execution stack at the point of allocation.
    stack: typing.List[str]

    def to_json(self) -> T_JSON_DICT:
        json: T_JSON_DICT = dict()
        json['size'] = self.size
        json['total'] = self.total
        json['stack'] = [i for i in self.stack]
        return json

    @classmethod
    def from_json(cls, json: T_JSON_DICT) -> SamplingProfileNode:
        return cls(
            size=float(json['size']),
            total=float(json['total']),
            stack=[str(i) for i in json['stack']],
        )


@dataclass
class SamplingProfile:
    '''
    Array of heap profile samples.
    '''
    samples: typing.List[SamplingProfileNode]

    modules: typing.List[Module]

    def to_json(self) -> T_JSON_DICT:
        json: T_JSON_DICT = dict()
        json['samples'] = [i.to_json() for i in self.samples]
        json['modules'] = [i.to_json() for i in self.modules]
        return json

    @classmethod
    def from_json(cls, json: T_JSON_DICT) -> SamplingProfile:
        return cls(
            samples=[SamplingProfileNode.from_json(i) for i in json['samples']],
            modules=[Module.from_json(i) for i in json['modules']],
        )


@dataclass
class Module:
    '''
    Executable module information
    '''
    #: Name of the module.
    name: str

    #: UUID of the module.
    uuid: str

    #: Base address where the module is loaded into memory. Encoded as a decimal
    #: or hexadecimal (0x prefixed) string.
    base_address: str

    #: Size of the module in bytes.
    size: float

    def to_json(self) -> T_JSON_DICT:
        json: T_JSON_DICT = dict()
        json['name'] = self.name
        json['uuid'] = self.uuid
        json['baseAddress'] = self.base_address
        json['size'] = self.size
        return json

    @classmethod
    def from_json(cls, json: T_JSON_DICT) -> Module:
        return cls(
            name=str(json['name']),
            uuid=str(json['uuid']),
            base_address=str(json['baseAddress']),
            size=float(json['size']),
        )


def get_dom_counters() -> typing.Generator[T_JSON_DICT,T_JSON_DICT,typing.Tuple[int, int, int]]:
    '''


    :returns: A tuple with the following items:

        0. **documents** - 
        1. **nodes** - 
        2. **jsEventListeners** - 
    '''
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.getDOMCounters',
    }
    json = yield cmd_dict
    return (
        int(json['documents']),
        int(json['nodes']),
        int(json['jsEventListeners'])
    )


def prepare_for_leak_detection() -> typing.Generator[T_JSON_DICT,T_JSON_DICT,None]:

    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.prepareForLeakDetection',
    }
    json = yield cmd_dict


def forcibly_purge_java_script_memory() -> typing.Generator[T_JSON_DICT,T_JSON_DICT,None]:
    '''
    Simulate OomIntervention by purging V8 memory.
    '''
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.forciblyPurgeJavaScriptMemory',
    }
    json = yield cmd_dict


def set_pressure_notifications_suppressed(
        suppressed: bool
    ) -> typing.Generator[T_JSON_DICT,T_JSON_DICT,None]:
    '''
    Enable/disable suppressing memory pressure notifications in all processes.

    :param suppressed: If true, memory pressure notifications will be suppressed.
    '''
    params: T_JSON_DICT = dict()
    params['suppressed'] = suppressed
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.setPressureNotificationsSuppressed',
        'params': params,
    }
    json = yield cmd_dict


def simulate_pressure_notification(
        level: PressureLevel
    ) -> typing.Generator[T_JSON_DICT,T_JSON_DICT,None]:
    '''
    Simulate a memory pressure notification in all processes.

    :param level: Memory pressure level of the notification.
    '''
    params: T_JSON_DICT = dict()
    params['level'] = level.to_json()
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.simulatePressureNotification',
        'params': params,
    }
    json = yield cmd_dict


def start_sampling(
        sampling_interval: typing.Optional[int] = None,
        suppress_randomness: typing.Optional[bool] = None
    ) -> typing.Generator[T_JSON_DICT,T_JSON_DICT,None]:
    '''
    Start collecting native memory profile.

    :param sampling_interval: *(Optional)* Average number of bytes between samples.
    :param suppress_randomness: *(Optional)* Do not randomize intervals between samples.
    '''
    params: T_JSON_DICT = dict()
    if sampling_interval is not None:
        params['samplingInterval'] = sampling_interval
    if suppress_randomness is not None:
        params['suppressRandomness'] = suppress_randomness
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.startSampling',
        'params': params,
    }
    json = yield cmd_dict


def stop_sampling() -> typing.Generator[T_JSON_DICT,T_JSON_DICT,None]:
    '''
    Stop collecting native memory profile.
    '''
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.stopSampling',
    }
    json = yield cmd_dict


def get_all_time_sampling_profile() -> typing.Generator[T_JSON_DICT,T_JSON_DICT,SamplingProfile]:
    '''
    Retrieve native memory allocations profile
    collected since renderer process startup.

    :returns: 
    '''
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.getAllTimeSamplingProfile',
    }
    json = yield cmd_dict
    return SamplingProfile.from_json(json['profile'])


def get_browser_sampling_profile() -> typing.Generator[T_JSON_DICT,T_JSON_DICT,SamplingProfile]:
    '''
    Retrieve native memory allocations profile
    collected since browser process startup.

    :returns: 
    '''
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.getBrowserSamplingProfile',
    }
    json = yield cmd_dict
    return SamplingProfile.from_json(json['profile'])


def get_sampling_profile() -> typing.Generator[T_JSON_DICT,T_JSON_DICT,SamplingProfile]:
    '''
    Retrieve native memory allocations profile collected since last
    ``startSampling`` call.

    :returns: 
    '''
    cmd_dict: T_JSON_DICT = {
        'method': 'Memory.getSamplingProfile',
    }
    json = yield cmd_dict
    return SamplingProfile.from_json(json['profile'])