from datetime import datetime, timedelta
import re
from exceptions import BeautySalonError, RoundMinuteError, TimeSlotNotAvailableError, ServiceNotProvidedError, ValidationError


class Client:
    def __init__(self, client_id, name, phone, email=None):
        self.client_id = client_id
        self.name = name
        self.phone = phone
        self.email = email
        self.visits_history = []

    def add_visit(self, visit):
        self.visits_history.append(visit)

    def get_visit_history(self):
        return self.visits_history

    def __str__(self):
        return f"Клиент: {self.name}, Телефон: {self.phone}"


class Service:
    def __init__(self, service_id, name, duration, price, category):
        self.service_id = service_id
        self.name = name
        self.duration = duration  # в минутах
        self.price = price
        self.category = category  # 'hair', 'nails', 'cosmetology' etc.

    def __str__(self):
        return f"{self.name} - {self.duration} мин. - {self.price} руб."


class Master:
    def __init__(self, master_id, name, specialization, phone, break_duration=10):
        self.master_id = master_id
        self.name = name
        self.specialization = specialization
        self.phone = phone
        self.schedule = {}  # {дата: {время: (длительность, тип_записи)}}
        self.break_duration = break_duration

    def is_available(self, date, time, duration):
        """Проверяет доступность мастера с учетом конкретной длительности услуги"""
        if date not in self.schedule:
            return True

        new_start = datetime.strptime(time, "%H:%M")
        new_end = new_start + timedelta(minutes=duration)

        # Проверяем все существующие записи на эту дату
        for booked_time, (booked_duration, _) in self.schedule[date].items():
            booked_start = datetime.strptime(booked_time, "%H:%M")
            booked_end = booked_start + timedelta(minutes=booked_duration)

            # Проверяем пересечение интервалов
            if not (new_end <= booked_start or new_start >= booked_end):
                return False

        return True

    def add_appointment(self, date, time, duration):
        """Добавляет запись с указанием длительности"""
        if date not in self.schedule:
            self.schedule[date] = {}

        # Добавляем основную запись
        self.schedule[date][time] = (duration, "service")

        # Добавляем перерыв после услуги
        start_time = datetime.strptime(time, "%H:%M")
        break_time = start_time + timedelta(minutes=duration)
        break_time_str = break_time.strftime("%H:%M")
        self.schedule[date][break_time_str] = (self.break_duration, "break")

        # Сортируем расписание для удобства
        self.schedule[date] = dict(sorted(self.schedule[date].items()))

    def get_busy_intervals(self, date):
        """Возвращает список занятых интервалов на указанную дату"""
        if date not in self.schedule:
            return []

        busy_intervals = []
        for time, (duration, record_type) in sorted(self.schedule[date].items()):
            start_time = datetime.strptime(time, "%H:%M")
            end_time = start_time + timedelta(minutes=duration)
            busy_intervals.append((start_time, end_time, record_type))
        return busy_intervals

    def __str__(self):
        return f"Мастер: {self.name} ({', '.join(self.specialization)})"


class Appointment:
    def __init__(self, appointment_id, client, master, service, date, time_slot):
        self.appointment_id = appointment_id
        self.client = client
        self.master = master
        self.service = service
        self.date = date
        self.time_slot = time_slot
        self.status = "confirmed"

    def cancel(self):
        self.status = "cancelled"
        # Освобождаем время у мастера
        date_schedule = self.master.schedule.get(self.date, {})

        # Удаляем основную запись
        if self.time_slot in date_schedule:
            del date_schedule[self.time_slot]

        # Удаляем перерыв после услуги
        start_time = datetime.strptime(self.time_slot, "%H:%M")
        break_time = start_time + timedelta(minutes=self.service.duration)
        break_time_str = break_time.strftime("%H:%M")

        if break_time_str in date_schedule:
            del date_schedule[break_time_str]

    def complete(self):
        self.status = "completed"

    def __str__(self):
        return f"Запись #{self.appointment_id}: {self.client.name} -> {self.master.name} ({self.service.name}) {self.date} {self.time_slot}"


class TimeValidator:
    @staticmethod
    def validate_time_format(time_str):
        """Проверяет формат времени HH:MM"""
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(pattern, time_str):
            raise ValidationError(f"Неверный формат времени: {time_str}. Используйте HH:MM")
        return True

    @staticmethod
    def validate_round_minutes(time_str):
        """Проверяет, что минуты кратны 5"""
        minutes = int(time_str.split(':')[1])
        if minutes % 5 != 0:
            raise RoundMinuteError(time_str)
        return True

    @staticmethod
    def validate_future_date(date_str):
        """Проверяет, что дата не в прошлом"""
        appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if appointment_date < datetime.now().date():
            raise ValidationError("Нельзя записаться на прошедшую дату")
        return True


class BeautySalon:
    def __init__(self, name):
        self.name = name
        self.clients = {}
        self.services = {}
        self.masters = {}
        self.appointments = {}
        self.next_client_id = 1
        self.next_service_id = 1
        self.next_master_id = 1
        self.next_appointment_id = 1
        self.validator = TimeValidator()

    def add_client(self, name, phone, email=None):
        client = Client(self.next_client_id, name, phone, email)
        self.clients[self.next_client_id] = client
        self.next_client_id += 1
        return client

    def add_service(self, name, duration, price, category):
        service = Service(self.next_service_id, name, duration, price, category)
        self.services[self.next_service_id] = service
        self.next_service_id += 1
        return service

    def add_master(self, name, specialization, phone, break_duration=10):
        master = Master(self.next_master_id, name, specialization, phone, break_duration)
        self.masters[self.next_master_id] = master
        self.next_master_id += 1
        return master

    def create_appointment(self, client_id, master_id, service_id, date, time_slot):
        try:
            # Валидация времени
            self.validator.validate_time_format(time_slot)
            self.validator.validate_round_minutes(time_slot)
            self.validator.validate_future_date(date)

            client = self.clients.get(client_id)
            master = self.masters.get(master_id)
            service = self.services.get(service_id)

            if not all([client, master, service]):
                return None, "Не найдены клиент, мастер или услуга."

            if service.name not in master.specialization:
                raise ServiceNotProvidedError(master.name, service.name)

            # Проверяем доступность с учетом КОНКРЕТНОЙ ДЛИТЕЛЬНОСТИ услуги
            if not master.is_available(date, time_slot, service.duration):
                raise TimeSlotNotAvailableError(time_slot, date)

            appointment = Appointment(self.next_appointment_id, client, master, service, date, time_slot)
            self.appointments[self.next_appointment_id] = appointment
            master.add_appointment(date, time_slot, service.duration)  # передаем длительность!
            client.add_visit(appointment)

            self.next_appointment_id += 1
            return appointment, "Запись создана успешно"

        except BeautySalonError as e:
            return None, str(e)

    def cancel_appointment(self, appointment_id):
        appointment = self.appointments.get(appointment_id)
        if appointment:
            appointment.cancel()
            return True, "Запись отменена"
        return False, "Запись не найдена"

    def get_master_schedule(self, master_id, date):
        """Возвращает расписание мастера на указанную дату"""
        master = self.masters.get(master_id)
        if master and date in master.schedule:
            schedule_info = []
            for time, (duration, record_type) in master.schedule[date].items():
                if record_type == "service":
                    schedule_info.append(f"{time} ({duration} мин)")
                else:
                    schedule_info.append(f"{time} (перерыв)")
            return schedule_info
        return []

    def get_client_appointments(self, client_id):
        client = self.clients.get(client_id)
        if client:
            return client.get_visit_history()
        return []

    def get_available_time_slots(self, master_id, date, service_duration):
        """Возвращает доступные временные слоты для мастера с учетом конкретной длительности услуги"""
        master = self.masters.get(master_id)
        if not master:
            return []

        available_slots = []

        # Рабочий день с 9:00 до 21:00
        start_time = datetime.strptime("09:00", "%H:%M")
        end_time = datetime.strptime("21:00", "%H:%M")

        current_time = start_time
        while current_time + timedelta(minutes=service_duration) <= end_time:
            time_slot = current_time.strftime("%H:%M")

            # Проверяем доступность с учетом КОНКРЕТНОЙ ДЛИТЕЛЬНОСТИ услуги
            if master.is_available(date, time_slot, service_duration):
                available_slots.append(time_slot)

            current_time += timedelta(minutes=15)  # проверяем каждые 15 минут

        return available_slots


def main():
    # Создаем салон
    salon = BeautySalon("Элит Салон")

    # Добавляем услуги
    haircut = salon.add_service("Стрижка", 60, 1500, "hair")
    coloring = salon.add_service("Окрашивание", 120, 3000, "hair")
    manicure = salon.add_service("Маникюр", 90, 2000, "nails")

    # Добавляем мастеров
    hair_master = salon.add_master("Анна", ["Стрижка", "Окрашивание"], "+79161234567")
    nails_master = salon.add_master("Мария", ["Маникюр"], "+79167654321")

    # Добавляем клиентов
    client1 = salon.add_client("Иван Петров", "+79031112233", "ivan@mail.com")
    client2 = salon.add_client("Мария Сидорова", "+79032223344")

    # Тестирование создания записей
    try:
        appointment1, message1 = salon.create_appointment(
            client1.client_id, hair_master.master_id, haircut.service_id,
            "2024-01-15", "10:00"
        )
        print(message1)

        # Попытка записаться на некруглое время
        appointment2, message2 = salon.create_appointment(
            client2.client_id, nails_master.master_id, manicure.service_id,
            "2024-01-15", "11:07"  # Некруглое время!
        )
        print(message2)

    except Exception as e:
        print(f"Ошибка: {e}")

    # Просмотр расписания мастера
    print(f"Занятое время у Анны: {salon.get_master_schedule(hair_master.master_id, '2024-01-15')}")

    # Получение доступных слотов
    available_slots = salon.get_available_time_slots(hair_master.master_id, "2024-01-15", 60)
    print(f"Доступные слоты: {available_slots[:5]}...")  # покажем первые 5


if __name__ == "__main__":
    main()
