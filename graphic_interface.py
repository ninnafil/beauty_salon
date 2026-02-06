import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from salon import BeautySalon, TimeValidator
from exceptions import BeautySalonError

class BeautySalonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Система записи в салон красоты")
        self.root.geometry("800x600")
        
        self.salon = BeautySalon("Элит Салон")
        self.validator = TimeValidator()
        self.setup_salon_data()
        self.create_widgets()
        
    def setup_salon_data(self):
        """Наполняем салон тестовыми данными"""
        # Услуги
        self.haircut_women = self.salon.add_service("Женская стрижка", 90, 2500, "hair")
        self.haircut_men = self.salon.add_service("Мужская стрижка", 60, 1500, "hair")
        self.haircut_child = self.salon.add_service("Детская стрижка", 45, 1200, "hair")
        self.hair_coloring = self.salon.add_service("Окрашивание волос", 180, 5000, "hair")
        self.keratin = self.salon.add_service("Кератиновое выпрямление", 150, 6000, "hair")
        self.lamination = self.salon.add_service("Ламинирование волос", 120, 4500, "hair")
        self.hair_styling = self.salon.add_service("Укладка", 60, 2000, "hair")
        self.wedding_hairstyle = self.salon.add_service("Свадебная прическа", 120, 8000, "hair")
        self.manicure = self.salon.add_service("Маникюр", 90, 3500, "nails")
        self.pedicure = self.salon.add_service("Педикюр", 90, 3000, "nails")
        self.face_cleaning = self.salon.add_service("Чистка лица", 90, 4000, "cosmetology")
        self.face_massage = self.salon.add_service("Массаж лица", 60, 3000, "cosmetology")
        self.peeling = self.salon.add_service("Пилинг", 60, 3500, "cosmetology")
        self.eyebrows_correction = self.salon.add_service("Коррекция бровей", 30, 800, "cosmetology")
        self.lash_lifting = self.salon.add_service("Ламинирование ресниц", 90, 3500, "cosmetology")
        self.sugar_epilation = self.salon.add_service("Депиляция комплекс", 75, 4000, "depilation")
        self.waxing_legs = self.salon.add_service("Восковая депиляция ног", 60, 2500, "depilation")
        self.waxing_bikini = self.salon.add_service("Депиляция зоны бикини", 45, 2500, "depilation")
        self.waxing_underarms = self.salon.add_service("Депиляция подмышек", 20, 1000, "depilation")
        
        # Мастера
        self.master_anna = self.salon.add_master(
            "Анна Волкова",
            ["Женская стрижка", "Окрашивание волос", "Укладка"],
            "+79161234567"
        )
        self.master_maria = self.salon.add_master(
            "Мария Смирнова",
            ["Женская стрижка", "Кератиновое выпрямление", "Ламинирование волос", "Свадебная прическа"],
            "+79162345678"
        )
        self.master_alex = self.salon.add_master(
            "Алексей Петров", 
            ["Мужская стрижка", "Детская стрижка", "Бритье"],
            "+79163456789"
        )
        self.master_olga = self.salon.add_master(
            "Ольга Козлова", 
            ["Окрашивание волос", "Кератиновое выпрямление"],
            "+79164567890"
        )
        self.master_irina = self.salon.add_master(
            "Ирина Новикова", 
            ["Маникюр", "Педикюр"],
            "+79165678901"
        )
        self.master_ekaterina = self.salon.add_master(
            "Екатерина Морозова", 
            ["Маникюр", "Педикюр"],
            "+79166789012"
        )
        self.master_elena = self.salon.add_master(
            "Елена Ковалева", 
            ["Чистка лица", "Массаж лица", "Пилинг", "Депиляция комплекс", "Восковая депиляция ног", "Депиляция зоны бикини", "Депиляция подмышек"],
            "+79168901234"
        )
        self.master_tatiana = self.salon.add_master(
            "Татьяна Федорова", 
            ["Коррекция бровей", "Ламинирование ресниц"],
            "+79169012345"
        )
        
        # Клиенты
        self.client1 = self.salon.add_client("Иван Петров", "+79031112233", "ivan@mail.com")
        self.client2 = self.salon.add_client("Мария Сидорова", "+79032223344")
        
    def create_widgets(self):
        # Создаем notebook для вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка записи
        self.create_booking_tab(notebook)
        
        # Вкладка просмотра записей
        self.create_appointments_tab(notebook)
        
        # Вкладка управления
        self.create_management_tab(notebook)
        
    def create_booking_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Новая запись")
        
        # Клиент
        ttk.Label(frame, text="Клиент:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.client_var = tk.StringVar()
        self.client_combo = ttk.Combobox(frame, textvariable=self.client_var, state="readonly")
        self.update_client_combo()
        self.client_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.client_combo.bind('<<ComboboxSelected>>', self.on_client_select)
        
        # Услуга
        ttk.Label(frame, text="Услуга:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.service_var = tk.StringVar()
        self.service_combo = ttk.Combobox(frame, textvariable=self.service_var, state="readonly")
        self.service_combo['values'] = [f"{s.service_id}: {s.name} ({s.duration} мин)" 
                                       for s in self.salon.services.values()]
        self.service_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.service_combo.bind('<<ComboboxSelected>>', self.on_service_select)
        
        # Мастер
        ttk.Label(frame, text="Мастер:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.master_var = tk.StringVar()
        self.master_combo = ttk.Combobox(frame, textvariable=self.master_var, state="readonly")
        self.master_combo.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        # Дата
        ttk.Label(frame, text="Дата:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = ttk.Entry(frame, textvariable=self.date_var)
        date_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        # Время
        ttk.Label(frame, text="Время:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.time_var = tk.StringVar()
        self.time_combo = ttk.Combobox(frame, textvariable=self.time_var, state="readonly")
        self.time_combo.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        
        # Кнопка поиска доступного времени
        ttk.Button(frame, text="Найти доступное время", 
                  command=self.find_available_time).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Кнопка создания записи
        ttk.Button(frame, text="Создать запись", 
                  command=self.create_appointment).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Статус
        self.status_label = ttk.Label(frame, text="", foreground="blue")
        self.status_label.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Настройка веса колонок для правильного растяжения
        frame.columnconfigure(1, weight=1)
        
    def create_appointments_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Мои записи")
        
        # Список записей
        self.appointments_tree = ttk.Treeview(frame, columns=('ID', 'Клиент', 'Мастер', 'Услуга', 'Дата', 'Время', 'Статус'), show='headings')
        
        columns = {
            'ID': 50,
            'Клиент': 120,
            'Мастер': 120,
            'Услуга': 150,
            'Дата': 100,
            'Время': 80,
            'Статус': 100
        }
        
        for col, width in columns.items():
            self.appointments_tree.heading(col, text=col)
            self.appointments_tree.column(col, width=width)
        
        self.appointments_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Обновить список", 
                  command=self.refresh_appointments).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отменить запись", 
                  command=self.cancel_selected_appointment).pack(side='left', padx=5)
        
    def create_management_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Управление")
        
        # Добавление нового клиента
        ttk.Label(frame, text="Добавить нового клиента", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Имя:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.new_client_name = ttk.Entry(frame, width=30)
        self.new_client_name.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(frame, text="Телефон:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.new_client_phone = ttk.Entry(frame, width=30)
        self.new_client_phone.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(frame, text="Email:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.new_client_email = ttk.Entry(frame, width=30)
        self.new_client_email.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Button(frame, text="Добавить клиента", 
                  command=self.add_new_client).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Настройка веса колонок
        frame.columnconfigure(1, weight=1)
        
    def update_client_combo(self):
        """Обновляет список клиентов в выпадающем меню"""
        clients_list = [f"{c.client_id}: {c.name} ({c.phone})" for c in self.salon.clients.values()]
        self.client_combo['values'] = clients_list
        if clients_list:
            self.client_combo.set(clients_list[0])
    
    def clear_booking_fields(self, clear_all=False):
        """
        Очищает поля формы записи
        clear_all: если True - очищает все поля, включая клиента и дату
        """
        if clear_all:
            # Полная очистка для нового клиента
            self.client_var.set('')
            self.client_combo.set('')
            self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        else:
            # Частичная очистка - оставляем клиента для повторной записи
            pass
        
        # Очищаем поля услуги, мастера и времени
        self.service_var.set('')
        self.master_var.set('')
        self.time_var.set('')
        
        self.service_combo.set('')
        self.master_combo.set('')
        self.time_combo.set('')
        self.time_combo['values'] = []
        
        self.status_label.config(text="Поля очищены. Можете создать новую запись.")

        def create_appointment(self):
            """Создает новую запись"""
            try:
                if not all([self.client_var.get(), self.service_var.get(), 
                        self.master_var.get(), self.date_var.get(), self.time_var.get()]):
                    messagebox.showerror("Ошибка", "Заполните все поля")
                    return
                    
                client_id = int(self.client_var.get().split(':')[0])
                master_id = int(self.master_var.get().split(':')[0])
                service_id = int(self.service_var.get().split(':')[0])
                
                appointment, message = self.salon.create_appointment(
                    client_id, master_id, service_id, 
                    self.date_var.get(), self.time_var.get()
                )
                
                if appointment:
                    messagebox.showinfo("Успех", message)
                    self.status_label.config(text="Запись создана успешно!")
                    self.refresh_appointments()
                    
                    # Спросим пользователя, хочет ли он очистить все поля
                    # или оставить клиента для повторной записи
                    response = messagebox.askyesno(
                        "Новая запись", 
                        "Запись создана успешно!\n\nОчистить все поля для нового клиента?\n\n" 
                        "НЕТ - оставить текущего клиента для повторной записи\n"
                        "ДА - очистить все поля"
                    )
                    
                    self.clear_booking_fields(clear_all=response)
                    
                else:
                    messagebox.showerror("Ошибка", message)
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при создании записи: {str(e)}")
        
    def on_client_select(self, event):
        self.update_masters()
        
    def on_service_select(self, event):
        self.update_masters()
        
    def update_masters(self):
        """Обновляет список мастеров в зависимости от выбранной услуги"""
        try:
            service_id = int(self.service_var.get().split(':')[0])
            service = self.salon.services.get(service_id)
            
            if service:
                available_masters = []
                for master in self.salon.masters.values():
                    if service.name in master.specialization:
                        available_masters.append(f"{master.master_id}: {master.name}")
                
                self.master_combo['values'] = available_masters
                if available_masters:
                    self.master_combo.set(available_masters[0])
        except (ValueError, IndexError):
            pass
        
    def find_available_time(self):
        """Находит доступное время для записи"""
        try:
            if not all([self.client_var.get(), self.service_var.get(), self.master_var.get(), self.date_var.get()]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
                
            master_id = int(self.master_var.get().split(':')[0])
            service_id = int(self.service_var.get().split(':')[0])
            service = self.salon.services.get(service_id)
            
            available_slots = self.salon.get_available_time_slots(
                master_id, self.date_var.get(), service.duration
            )
            
            self.time_combo['values'] = available_slots
            if available_slots:
                self.time_combo.set(available_slots[0])
                self.status_label.config(text=f"Найдено {len(available_slots)} доступных слотов")
            else:
                self.status_label.config(text="Нет доступных слотов на выбранную дату")
                self.time_combo.set('')
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске времени: {str(e)}")
            
    def create_appointment(self):
        """Создает новую запись"""
        try:
            if not all([self.client_var.get(), self.service_var.get(), 
                       self.master_var.get(), self.date_var.get(), self.time_var.get()]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
                
            client_id = int(self.client_var.get().split(':')[0])
            master_id = int(self.master_var.get().split(':')[0])
            service_id = int(self.service_var.get().split(':')[0])
            
            appointment, message = self.salon.create_appointment(
                client_id, master_id, service_id, 
                self.date_var.get(), self.time_var.get()
            )
            
            if appointment:
                messagebox.showinfo("Успех", message)
                self.status_label.config(text="Запись создана успешно!")
                self.refresh_appointments()
                # Очищаем поля после успешной записи
                self.time_var.set('')
            else:
                messagebox.showerror("Ошибка", message)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании записи: {str(e)}")
            
    def refresh_appointments(self):
        """Обновляет список записей"""
        for item in self.appointments_tree.get_children():
            self.appointments_tree.delete(item)
            
        for appointment in self.salon.appointments.values():
            self.appointments_tree.insert('', 'end', values=(
                appointment.appointment_id,
                appointment.client.name,
                appointment.master.name,
                appointment.service.name,
                appointment.date,
                appointment.time_slot,
                appointment.status
            ))
            
    def cancel_selected_appointment(self):
        """Отменяет выбранную запись"""
        selected = self.appointments_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для отмены")
            return
            
        appointment_id = int(self.appointments_tree.item(selected[0])['values'][0])
        success, message = self.salon.cancel_appointment(appointment_id)
        
        if success:
            messagebox.showinfo("Успех", message)
            self.refresh_appointments()
        else:
            messagebox.showerror("Ошибка", message)
            
    def add_new_client(self):
        """Добавляет нового клиента"""
        try:
            name = self.new_client_name.get().strip()
            phone = self.new_client_phone.get().strip()
            email = self.new_client_email.get().strip() or None
            
            if not name:
                messagebox.showerror("Ошибка", "Введите имя клиента")
                return
                
            if not phone:
                messagebox.showerror("Ошибка", "Введите телефон клиента")
                return
            
            # Проверяем формат телефона (простая проверка)
            if len(phone) < 5:
                messagebox.showerror("Ошибка", "Телефон слишком короткий")
                return
            
            # Добавляем клиента
            client = self.salon.add_client(name, phone, email)
            messagebox.showinfo("Успех", f"Клиент '{client.name}' успешно добавлен!")
            
            # Очищаем поля
            self.new_client_name.delete(0, tk.END)
            self.new_client_phone.delete(0, tk.END)
            self.new_client_email.delete(0, tk.END)
            
            # Обновляем список клиентов в комбобоксе
            self.update_client_combo()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении клиента: {str(e)}")

def main():
    root = tk.Tk()
    app = BeautySalonGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()