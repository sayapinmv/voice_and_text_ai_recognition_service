from abc import ABC, abstractmethod


class FieldSetting(ABC):

    @abstractmethod
    def setting_value(self, val): pass


class StrToBool(FieldSetting):

    def setting_value(self, val: str):
        if val.lower() == 'true':
            return True
        elif val.lower() == 'false':
            return False
        else:
            raise ValueError(f'Invalid bool value: {val}')
