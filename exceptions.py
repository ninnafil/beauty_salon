class BeautySalonError(Exception):
    """Базовое исключение для салона красоты"""
    pass


class TimeSlotError(BeautySalonError):
    """Ошибка временного слота"""
    pass


class RoundMinuteError(TimeSlotError):
    """Ошибка: время должно быть кратно 5 минутам"""
    def __init__(self, time_str):
        super().__init__(f"Время должно быть круглым числом минут (кратно 5). Получено: {time_str}")


class TimeSlotNotAvailableError(TimeSlotError):
    """Ошибка: временной слот занят"""
    def __init__(self, time_str):
        super().__init__(f"Данное время {time_str} занято.")


class ServiceNotProvidedError(BeautySalonError):
    """Ошибка: мастер не предоставляет услугу"""
    def __init__(self, master_name, service_name):
        super().__init__(f"Мастер {master_name} не предоставляет услугу '{service_name}'")


class ValidationError(BeautySalonError):
    """Ошибка валидации данных"""
    pass
