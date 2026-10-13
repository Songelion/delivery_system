"""
GUI-интерфейс для системы доставки.
Две вкладки: Заказы, Клиенты.
Фичи: список товаров в заказе, фильтр по дате, период в отчёте, экспорт/импорт.
Стиль: розовая тема, шрифт Times New Roman.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, timedelta

from database import (
    get_all_orders,
    get_customer_by_id,
    get_orders_by_status,
    get_orders_by_date,
    add_order,
    update_order,
    delete_order,
    get_order_by_id,
    get_all_customers,
    get_customer_by_id as get_customer,
    add_customer,
    update_customer,
    delete_customer,
    add_order_item,
    get_items_by_order,
    delete_order_item,
    report_by_status,
    report_top_customers,
    report_revenue,
)
from data_export import export_to_json, import_from_json
from logger_config import setup_logger


log = setup_logger()


# ============================================================
# Цвета и шрифты
# ============================================================

COLOR_BG = '#f5cced'
COLOR_PINK = '#ddacd3'
COLOR_PINK_DARK = '#f5e0f1'
COLOR_TEXT = '#973561'
COLOR_FIELD = '#fdebd8'
COLOR_TABLE_HEAD = '#ffb6c1'
COLOR_WHITE = '#ffffff'

FONT = 'Times New Roman'
FONT_NORMAL = (FONT, 12)
FONT_BOLD = (FONT, 12, 'bold')
FONT_TITLE = (FONT, 18, 'bold')
FONT_SMALL = (FONT, 11)
FONT_MONO = ('Courier New', 11)


# ============================================================
# Главное приложение
# ============================================================

class DeliveryApp:
    """Главное приложение."""
    
    def __init__(self, root):
        self.root = root
        self.root.title('Быстрая доставка — Учёт заказов')
        self.root.geometry('1000x700')
        self.root.configure(bg=COLOR_BG)
        
        log.info('GUI запущен')
        
        self._setup_style()
        self._create_widgets()
        self.refresh_orders()
        self.refresh_customers()
    
    def _setup_style(self):
        """Настроить ttk-стили."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Treeview
        style.configure(
            'Custom.Treeview',
            background=COLOR_FIELD,
            foreground=COLOR_TEXT,
            fieldbackground=COLOR_FIELD,
            font=FONT_NORMAL,
            rowheight=28,
            bordercolor=COLOR_PINK,
            lightcolor=COLOR_PINK,
            darkcolor=COLOR_PINK
        )
        style.configure(
            'Custom.Treeview.Heading',
            background=COLOR_TABLE_HEAD,
            foreground=COLOR_TEXT,
            font=FONT_BOLD,
            bordercolor=COLOR_PINK,
            lightcolor=COLOR_PINK,
            darkcolor=COLOR_PINK
        )
        style.map('Custom.Treeview', background=[('selected', COLOR_PINK)])
        
        # Combobox
        style.configure(
            'Custom.TCombobox',
            fieldbackground=COLOR_WHITE,
            background=COLOR_WHITE,
            foreground=COLOR_TEXT,
            arrowcolor=COLOR_TEXT,
            bordercolor=COLOR_PINK,
            lightcolor=COLOR_WHITE,
            darkcolor=COLOR_WHITE,
            font=FONT_NORMAL
        )
        style.map(
            'Custom.TCombobox',
            fieldbackground=[
                ('readonly', COLOR_WHITE),
                ('!disabled', COLOR_WHITE),
                ('active', COLOR_WHITE),
                ('focus', COLOR_WHITE),
            ],
            background=[
                ('readonly', COLOR_WHITE),
                ('!disabled', COLOR_WHITE),
                ('active', COLOR_WHITE),
                ('focus', COLOR_WHITE),
            ],
            foreground=[
                ('readonly', COLOR_TEXT),
                ('!disabled', COLOR_TEXT),
            ],
        )
        
        self.root.option_add('*TCombobox*Listbox.background', COLOR_WHITE)
        self.root.option_add('*TCombobox*Listbox.foreground', COLOR_TEXT)
        self.root.option_add('*TCombobox*Listbox.selectBackground', COLOR_PINK)
        self.root.option_add('*TCombobox*Listbox.selectForeground', COLOR_TEXT)
        self.root.option_add('*TCombobox*Listbox.font', FONT_NORMAL)
        
        # Scrollbar
        style.configure(
            'Custom.Vertical.TScrollbar',
            background=COLOR_PINK,
            troughcolor=COLOR_FIELD,
            bordercolor=COLOR_PINK,
            arrowcolor=COLOR_TEXT,
            lightcolor=COLOR_PINK,
            darkcolor=COLOR_PINK
        )
        
        # Notebook
        style.configure(
            'Custom.TNotebook',
            background=COLOR_BG,
            bordercolor=COLOR_PINK,
            lightcolor=COLOR_PINK,
            darkcolor=COLOR_PINK
        )
        style.configure(
            'Custom.TNotebook.Tab',
            background=COLOR_PINK_DARK,
            foreground=COLOR_TEXT,
            padding=[25, 8],
            font=(FONT, 12, 'bold'),
            bordercolor=COLOR_PINK,
            lightcolor=COLOR_PINK,
            darkcolor=COLOR_PINK
        )
        style.map(
            'Custom.TNotebook.Tab',
            background=[('selected', COLOR_PINK)],
            foreground=[('selected', COLOR_TEXT)],
            padding=[('selected', [50, 18])],
            font=[('selected', (FONT, 15, 'bold'))],
            expand=[('selected', [0, 0, 0, 0])]
        )
    
    def _make_button(self, parent, text, command, width=15):
        """Розовая кнопка через Label."""
        lbl = tk.Label(
            parent,
            text=text,
            font=FONT_NORMAL,
            bg=COLOR_PINK,
            fg=COLOR_TEXT,
            width=width,
            padx=5,
            pady=5,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        )
        lbl.pack(side=tk.LEFT, padx=3)
        lbl.bind('<Button-1>', lambda e: command())
        return lbl
    
    def _create_widgets(self):
        """Создать все элементы интерфейса."""
        # ===== Заголовок =====
        title = tk.Label(
            self.root,
            text='Быстрая доставка',
            font=FONT_TITLE,
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            pady=15
        )
        title.pack()
        
        # ===== Вкладки =====
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tab_orders = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_orders, text='Заказы')
        self._create_orders_tab()
        
        self.tab_customers = tk.Frame(self.notebook, bg=COLOR_BG)
        self.notebook.add(self.tab_customers, text='Клиенты')
        self._create_customers_tab()
        
        # ===== Статус-бар =====
        self.status_var = tk.StringVar()
        self.status_var.set('Готово')
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor='w',
            font=FONT_SMALL,
            bg=COLOR_PINK,
            fg=COLOR_TEXT,
            padx=10,
            pady=3
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # ===== Цветочек =====
        sakura_label = tk.Label(
            self.root,
            text='🌸',
            font=('Arial', 24),
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            bd=0,
            highlightthickness=0
        )
        sakura_label.place(relx=1.0, rely=0.0, anchor='ne', x=-15, y=8)
    
    # ========================================================
    # Вкладка «Заказы»
    # ========================================================
    
    def _create_orders_tab(self):
        """Создать содержимое вкладки «Заказы»."""
        # ===== Панель кнопок =====
        button_frame = tk.Frame(self.tab_orders, bg=COLOR_BG)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._make_button(button_frame, 'Добавить', self.on_add_order, 13)
        self._make_button(button_frame, 'Редактировать', self.on_edit_order, 13)
        self._make_button(button_frame, 'Удалить', self.on_delete_order, 10)
        self._make_button(button_frame, 'Обновить', self.refresh_orders, 10)
        self._make_button(button_frame, 'Показать отчёт', self.on_report, 15)
        self._make_button(button_frame, 'Экспорт', self.on_export, 10)
        self._make_button(button_frame, 'Импорт', self.on_import, 10)
        
        # ===== Панель фильтров =====
        filter_frame = tk.Frame(self.tab_orders, bg=COLOR_BG)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            filter_frame, text='Статус:',
            font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_TEXT
        ).pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar(value='все')
        self.filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=['все', 'новый', 'в доставке', 'выполнен', 'отменён'],
            state='readonly',
            width=12,
            font=FONT_NORMAL,
            style='Custom.TCombobox'
        )
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            filter_frame, text='С:',
            font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_TEXT
        ).pack(side=tk.LEFT, padx=(15, 0))
        
        self.date_from_entry = tk.Entry(
            filter_frame, width=12, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.date_from_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            filter_frame, text='По:',
            font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_TEXT
        ).pack(side=tk.LEFT)
        
        self.date_to_entry = tk.Entry(
            filter_frame, width=12, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.date_to_entry.pack(side=tk.LEFT, padx=5)
        
        # Кнопки фильтра
        apply_btn = tk.Label(
            filter_frame, text='Применить',
            font=FONT_NORMAL, bg=COLOR_PINK, fg=COLOR_TEXT,
            width=12, padx=5, pady=3,
            relief=tk.RAISED, bd=2, cursor='hand2'
        )
        apply_btn.pack(side=tk.LEFT, padx=5)
        apply_btn.bind('<Button-1>', lambda e: self.refresh_orders())
        
        reset_btn = tk.Label(
            filter_frame, text='Сбросить',
            font=FONT_NORMAL, bg=COLOR_PINK_DARK, fg=COLOR_TEXT,
            width=12, padx=5, pady=3,
            relief=tk.RAISED, bd=2, cursor='hand2'
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        reset_btn.bind('<Button-1>', lambda e: self._reset_filters())
        
        # ===== Таблица заказов =====
        table_frame = tk.Frame(self.tab_orders, bg=COLOR_BG)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ('id', 'customer', 'date', 'status', 'total')
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show='headings',
            style='Custom.Treeview'
        )
        
        self.tree.heading('id', text='ID')
        self.tree.heading('customer', text='Клиент')
        self.tree.heading('date', text='Дата')
        self.tree.heading('status', text='Статус')
        self.tree.heading('total', text='Сумма, руб.')
        
        self.tree.column('id', width=50, anchor='center')
        self.tree.column('customer', width=250)
        self.tree.column('date', width=120, anchor='center')
        self.tree.column('status', width=120, anchor='center')
        self.tree.column('total', width=120, anchor='e')
        
        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL,
            command=self.tree.yview,
            style='Custom.Vertical.TScrollbar'
        )
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _reset_filters(self):
        """Сбросить фильтры."""
        self.filter_var.set('все')
        self.date_from_entry.delete(0, tk.END)
        self.date_to_entry.delete(0, tk.END)
        self.refresh_orders()
    
    # ========================================================
    # Вкладка «Клиенты»
    # ========================================================
    
    def _create_customers_tab(self):
        """Создать содержимое вкладки «Клиенты»."""
        button_frame = tk.Frame(self.tab_customers, bg=COLOR_BG)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._make_button(button_frame, 'Добавить', self.on_add_customer, 15)
        self._make_button(button_frame, 'Редактировать', self.on_edit_customer, 15)
        self._make_button(button_frame, 'Удалить', self.on_delete_customer, 15)
        self._make_button(button_frame, 'Обновить', self.refresh_customers, 15)
        
        table_frame = tk.Frame(self.tab_customers, bg=COLOR_BG)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ('id', 'name', 'phone', 'address')
        self.tree_customers = ttk.Treeview(
            table_frame, columns=columns, show='headings',
            style='Custom.Treeview'
        )
        
        self.tree_customers.heading('id', text='ID')
        self.tree_customers.heading('name', text='Имя')
        self.tree_customers.heading('phone', text='Телефон')
        self.tree_customers.heading('address', text='Адрес')
        
        self.tree_customers.column('id', width=50, anchor='center')
        self.tree_customers.column('name', width=200)
        self.tree_customers.column('phone', width=180)
        self.tree_customers.column('address', width=350)
        
        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL,
            command=self.tree_customers.yview,
            style='Custom.Vertical.TScrollbar'
        )
        self.tree_customers.configure(yscroll=scrollbar.set)
        
        self.tree_customers.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # ========================================================
    # Обработчики: Заказы
    # ========================================================
    
    def _get_selected_order_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning('Внимание', 'Выберите заказ в таблице')
            return None
        item = self.tree.item(selection[0])
        return item['values'][0]
    
    def on_add_order(self):
        OrderForm(self.root, on_save=self.refresh_orders)
    
    def on_edit_order(self):
        order_id = self._get_selected_order_id()
        if order_id is None:
            return
        OrderForm(self.root, order_id=order_id, on_save=self.refresh_orders)
    
    def on_delete_order(self):
        order_id = self._get_selected_order_id()
        if order_id is None:
            return
        
        answer = messagebox.askyesno(
            'Подтверждение',
            f'Удалить заказ id={order_id}?'
        )
        if not answer:
            return
        
        delete_order(order_id)
        log.info(f'Удалён заказ id={order_id}')
        self.refresh_orders()
    
    def on_report(self):
        ReportWindow(self.root)
    
    def on_export(self):
        """Экспорт заказов в JSON."""
        filename = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
            initialfile='orders_backup.json'
        )
        if not filename:
            return
        
        try:
            count = export_to_json(filename)
            messagebox.showinfo('Экспорт', f'Экспортировано {count} заказов')
            log.info(f'Экспортировано {count} заказов в {filename}')
        except Exception as e:
            messagebox.showerror('Ошибка экспорта', str(e))
            log.error(f'Ошибка экспорта: {e}')
    
    def on_import(self):
        """Импорт заказов из JSON."""
        filename = filedialog.askopenfilename(
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')]
        )
        if not filename:
            return
        
        try:
            count = import_from_json(filename)
            messagebox.showinfo('Импорт', f'Импортировано {count} заказов')
            log.info(f'Импортировано {count} заказов из {filename}')
            self.refresh_orders()
        except Exception as e:
            messagebox.showerror('Ошибка импорта', str(e))
            log.error(f'Ошибка импорта: {e}')
    
    def refresh_orders(self):
        """Обновить таблицу заказов (с учётом фильтров)."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        filter_value = self.filter_var.get()
        date_from = self.date_from_entry.get().strip()
        date_to = self.date_to_entry.get().strip()
        
        # Логика фильтрации
        if date_from and date_to:
            orders = get_orders_by_date(date_from, date_to)
            if filter_value != 'все':
                orders = [o for o in orders if o.status == filter_value]
        elif filter_value != 'все':
            orders = get_orders_by_status(filter_value)
        else:
            orders = get_all_orders()
        
        for order in orders:
            customer = get_customer_by_id(order.customer_id)
            customer_name = customer.name if customer else f'<id={order.customer_id}>'
            
            self.tree.insert('', tk.END, values=(
                order.id,
                customer_name,
                order.order_date,
                order.status,
                f'{order.total:.2f}'
            ))
        
        self.status_var.set(f'Заказов: {len(orders)}')
    
    # ========================================================
    # Обработчики: Клиенты
    # ========================================================
    
    def _get_selected_customer_id(self):
        selection = self.tree_customers.selection()
        if not selection:
            messagebox.showwarning('Внимание', 'Выберите клиента в таблице')
            return None
        item = self.tree_customers.item(selection[0])
        return item['values'][0]
    
    def on_add_customer(self):
        CustomerForm(self.root, on_save=self.refresh_customers)
    
    def on_edit_customer(self):
        customer_id = self._get_selected_customer_id()
        if customer_id is None:
            return
        CustomerForm(self.root, customer_id=customer_id, on_save=self.refresh_customers)
    
    def on_delete_customer(self):
        customer_id = self._get_selected_customer_id()
        if customer_id is None:
            return
        
        answer = messagebox.askyesno(
            'Подтверждение',
            f'Удалить клиента id={customer_id}?'
        )
        if not answer:
            return
        
        try:
            delete_customer(customer_id)
            log.info(f'Удалён клиент id={customer_id}')
            self.refresh_customers()
        except ValueError as e:
            messagebox.showerror('Ошибка удаления', str(e))
            log.warning(f'Ошибка удаления клиента: {e}')
    
    def refresh_customers(self):
        """Обновить таблицу клиентов."""
        for row in self.tree_customers.get_children():
            self.tree_customers.delete(row)
        
        customers = get_all_customers()
        
        for customer in customers:
            self.tree_customers.insert('', tk.END, values=(
                customer.id,
                customer.name,
                customer.phone or '—',
                customer.address or '—'
            ))
        
        self.status_var.set(f'Клиентов: {len(customers)}')


# ============================================================
# Форма заказа (с товарами)
# ============================================================

class OrderForm:
    """Окно формы добавления/редактирования заказа."""
    
    def __init__(self, parent, order_id=None, on_save=None):
        self.order_id = order_id
        self.on_save = on_save
        self.items = []  # список dict: {id, product_name, quantity, price}
        
        self.window = tk.Toplevel(parent)
        self.window.title('Редактирование заказа' if order_id else 'Новый заказ')
        self.window.geometry('650x600')
        self.window.configure(bg=COLOR_BG)
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        
        if order_id is not None:
            self._load_order()
        
        self._update_total()
    
    def _create_widgets(self):
        frame = tk.Frame(self.window, padx=20, pady=15, bg=COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Клиент =====
        tk.Label(
            frame, text='Клиент:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(
            frame, textvariable=self.customer_var,
            state='readonly', width=35, font=FONT_NORMAL,
            style='Custom.TCombobox'
        )
        self.customer_combo.grid(row=0, column=1, pady=5, padx=5, columnspan=2, sticky='w')
        
        self.customers = get_all_customers()
        self.customer_combo['values'] = [c.name for c in self.customers]
        
        # ===== Дата =====
        tk.Label(
            frame, text='Дата:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        self.date_entry = tk.Entry(
            frame, width=37, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.date_entry.grid(row=1, column=1, pady=5, padx=5, columnspan=2, sticky='w')
        self.date_entry.insert(0, date.today().isoformat())
        
        # ===== Статус =====
        tk.Label(
            frame, text='Статус:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=2, column=0, sticky='w', pady=5)
        
        self.status_var = tk.StringVar(value='новый')
        self.status_combo = ttk.Combobox(
            frame, textvariable=self.status_var,
            values=['новый', 'в доставке', 'выполнен', 'отменён'],
            state='readonly', width=35, font=FONT_NORMAL,
            style='Custom.TCombobox'
        )
        self.status_combo.grid(row=2, column=1, pady=5, padx=5, columnspan=2, sticky='w')
        
        # ===== Разделитель =====
        tk.Frame(frame, bg=COLOR_PINK, height=2).grid(
            row=3, column=0, columnspan=3, sticky='ew', pady=10
        )
        
        tk.Label(
            frame, text='Товары в заказе:', font=FONT_BOLD,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=4, column=0, columnspan=3, sticky='w', pady=5)
        
        # ===== Таблица товаров =====
        items_frame = tk.Frame(frame, bg=COLOR_BG)
        items_frame.grid(row=5, column=0, columnspan=3, sticky='ew', pady=5)
        
        columns = ('product', 'quantity', 'price', 'sum')
        self.items_tree = ttk.Treeview(
            items_frame, columns=columns, show='headings',
            style='Custom.Treeview', height=6
        )
        
        self.items_tree.heading('product', text='Товар')
        self.items_tree.heading('quantity', text='Кол-во')
        self.items_tree.heading('price', text='Цена')
        self.items_tree.heading('sum', text='Сумма')
        
        self.items_tree.column('product', width=200)
        self.items_tree.column('quantity', width=70, anchor='center')
        self.items_tree.column('price', width=80, anchor='e')
        self.items_tree.column('sum', width=80, anchor='e')
        
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        
        # ===== Кнопки товаров =====
        items_buttons = tk.Frame(frame, bg=COLOR_BG)
        items_buttons.grid(row=6, column=0, columnspan=3, sticky='w', pady=5)
        
        add_item_btn = tk.Label(
            items_buttons, text='Добавить товар', font=FONT_NORMAL,
            bg=COLOR_PINK, fg=COLOR_TEXT, width=16,
            padx=5, pady=3, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        add_item_btn.pack(side=tk.LEFT, padx=3)
        add_item_btn.bind('<Button-1>', lambda e: self._add_item())
        
        del_item_btn = tk.Label(
            items_buttons, text='Удалить товар', font=FONT_NORMAL,
            bg=COLOR_PINK_DARK, fg=COLOR_TEXT, width=16,
            padx=5, pady=3, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        del_item_btn.pack(side=tk.LEFT, padx=3)
        del_item_btn.bind('<Button-1>', lambda e: self._delete_item())
        
        # ===== Итого =====
        self.total_label = tk.Label(
            frame, text='Итого: 0.00 руб.',
            font=FONT_BOLD, bg=COLOR_BG, fg=COLOR_TEXT
        )
        self.total_label.grid(row=7, column=0, columnspan=3, sticky='e', pady=10)
        
        # ===== Кнопки =====
        button_frame = tk.Frame(frame, bg=COLOR_BG)
        button_frame.grid(row=8, column=0, columnspan=3, pady=15)
        
        save_btn = tk.Label(
            button_frame, text='Сохранить', font=FONT_BOLD,
            bg=COLOR_PINK, fg=COLOR_TEXT, width=14,
            padx=5, pady=5, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        save_btn.bind('<Button-1>', lambda e: self._save())
        
        cancel_btn = tk.Label(
            button_frame, text='Отмена', font=FONT_NORMAL,
            bg=COLOR_PINK_DARK, fg=COLOR_TEXT, width=14,
            padx=5, pady=5, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn.bind('<Button-1>', lambda e: self.window.destroy())
    
    def _refresh_items_table(self):
        """Обновить таблицу товаров."""
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)
        
        for item in self.items:
            sum_val = item['quantity'] * item['price']
            self.items_tree.insert('', tk.END, values=(
                item['product_name'],
                item['quantity'],
                f'{item["price"]:.2f}',
                f'{sum_val:.2f}'
            ))
        
        self._update_total()
    
    def _update_total(self):
        """Обновить «Итого»."""
        total = sum(i['quantity'] * i['price'] for i in self.items)
        self.total_label.config(text=f'Итого: {total:.2f} руб.')
    
    def _add_item(self):
        """Открыть мини-форму добавления товара."""
        ItemForm(self.window, on_save=self._on_item_added)
    
    def _on_item_added(self, item_data):
        """Добавить товар в список."""
        self.items.append({
            'id': None,
            'product_name': item_data['product_name'],
            'quantity': item_data['quantity'],
            'price': item_data['price']
        })
        self._refresh_items_table()
    
    def _delete_item(self):
        """Удалить выбранный товар."""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning('Внимание', 'Выберите товар')
            return
        
        index = self.items_tree.index(selection[0])
        del self.items[index]
        self._refresh_items_table()
    
    def _load_order(self):
        """Загрузить заказ."""
        order = get_order_by_id(self.order_id)
        if order is None:
            messagebox.showerror('Ошибка', f'Заказ id={self.order_id} не найден')
            self.window.destroy()
            return
        
        for c in self.customers:
            if c.id == order.customer_id:
                self.customer_var.set(c.name)
                break
        
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, order.order_date)
        self.status_var.set(order.status)
        
        # Загружаем товары
        items = get_items_by_order(self.order_id)
        for item in items:
            self.items.append({
                'id': item.id,
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': item.price
            })
        
        self._refresh_items_table()
    
    def _save(self):
        """Сохранить заказ."""
        customer_name = self.customer_var.get()
        if not customer_name:
            messagebox.showwarning('Ошибка', 'Выберите клиента')
            return
        
        customer = None
        for c in self.customers:
            if c.name == customer_name:
                customer = c
                break
        
        if customer is None:
            messagebox.showwarning('Ошибка', 'Клиент не найден')
            return
        
        order_date = self.date_entry.get().strip()
        if not order_date:
            messagebox.showwarning('Ошибка', 'Введите дату')
            return
        
        status = self.status_var.get()
        total = sum(i['quantity'] * i['price'] for i in self.items)
        
        try:
            if self.order_id is None:
                # Создание
                new_id = add_order(customer.id, order_date, status, total)
                # Добавляем товары
                for item in self.items:
                    add_order_item(
                        new_id,
                        item['product_name'],
                        item['quantity'],
                        item['price']
                    )
                log.info(f'Создан заказ id={new_id}')
            else:
                # Обновление
                update_order(
                    self.order_id,
                    customer_id=customer.id,
                    order_date=order_date,
                    status=status,
                    total=total
                )
                # Удаляем старые товары
                old_items = get_items_by_order(self.order_id)
                for old in old_items:
                    delete_order_item(old.id)
                # Добавляем новые
                for item in self.items:
                    add_order_item(
                        self.order_id,
                        item['product_name'],
                        item['quantity'],
                        item['price']
                    )
                log.info(f'Обновлён заказ id={self.order_id}')
        except Exception as e:
            messagebox.showerror('Ошибка сохранения', str(e))
            return
        
        if self.on_save:
            self.on_save()
        
        self.window.destroy()


# ============================================================
# Мини-форма товара
# ============================================================

class ItemForm:
    """Мини-форма добавления товара."""
    
    def __init__(self, parent, on_save=None):
        self.on_save = on_save
        
        self.window = tk.Toplevel(parent)
        self.window.title('Новый товар')
        self.window.geometry('400x250')
        self.window.configure(bg=COLOR_BG)
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        frame = tk.Frame(self.window, padx=20, pady=20, bg=COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Название
        tk.Label(
            frame, text='Название:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=0, column=0, sticky='w', pady=8)
        
        self.name_entry = tk.Entry(
            frame, width=25, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.name_entry.grid(row=0, column=1, pady=8, padx=5)
        
        # Количество
        tk.Label(
            frame, text='Количество:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=1, column=0, sticky='w', pady=8)
        
        self.quantity_entry = tk.Entry(
            frame, width=25, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.quantity_entry.grid(row=1, column=1, pady=8, padx=5)
        self.quantity_entry.insert(0, '1')
        
        # Цена
        tk.Label(
            frame, text='Цена:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=2, column=0, sticky='w', pady=8)
        
        self.price_entry = tk.Entry(
            frame, width=25, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.price_entry.grid(row=2, column=1, pady=8, padx=5)
        self.price_entry.insert(0, '0.0')
        
        # Кнопки
        button_frame = tk.Frame(frame, bg=COLOR_BG)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        ok_btn = tk.Label(
            button_frame, text='OK', font=FONT_BOLD,
            bg=COLOR_PINK, fg=COLOR_TEXT, width=12,
            padx=5, pady=5, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        ok_btn.pack(side=tk.LEFT, padx=5)
        ok_btn.bind('<Button-1>', lambda e: self._save())
        
        cancel_btn = tk.Label(
            button_frame, text='Отмена', font=FONT_NORMAL,
            bg=COLOR_PINK_DARK, fg=COLOR_TEXT, width=12,
            padx=5, pady=5, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn.bind('<Button-1>', lambda e: self.window.destroy())
    
    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning('Ошибка', 'Введите название')
            return
        
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning('Ошибка', 'Количество — целое положительное число')
            return
        
        try:
            price = float(self.price_entry.get())
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning('Ошибка', 'Цена — неотрицательное число')
            return
        
        if self.on_save:
            self.on_save({
                'product_name': name,
                'quantity': quantity,
                'price': price
            })
        
        self.window.destroy()


# ============================================================
# Форма клиента
# ============================================================

class CustomerForm:
    """Окно формы добавления/редактирования клиента."""
    
    def __init__(self, parent, customer_id=None, on_save=None):
        self.customer_id = customer_id
        self.on_save = on_save
        
        self.window = tk.Toplevel(parent)
        self.window.title('Редактирование клиента' if customer_id else 'Новый клиент')
        self.window.geometry('480x320')
        self.window.configure(bg=COLOR_BG)
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        
        if customer_id is not None:
            self._load_customer()
    
    def _create_widgets(self):
        frame = tk.Frame(self.window, padx=20, pady=20, bg=COLOR_BG)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame, text='Имя*:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=0, column=0, sticky='w', pady=8)
        
        self.name_entry = tk.Entry(
            frame, width=30, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.name_entry.grid(row=0, column=1, pady=8, padx=5)
        
        tk.Label(
            frame, text='Телефон:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=1, column=0, sticky='w', pady=8)
        
        self.phone_entry = tk.Entry(
            frame, width=30, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.phone_entry.grid(row=1, column=1, pady=8, padx=5)
        
        tk.Label(
            frame, text='Адрес:', font=FONT_NORMAL,
            bg=COLOR_BG, fg=COLOR_TEXT
        ).grid(row=2, column=0, sticky='w', pady=8)
        
        self.address_entry = tk.Entry(
            frame, width=30, font=FONT_NORMAL,
            bg=COLOR_WHITE, fg=COLOR_TEXT, relief=tk.SUNKEN, bd=2
        )
        self.address_entry.grid(row=2, column=1, pady=8, padx=5)
        
        button_frame = tk.Frame(frame, bg=COLOR_BG)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        save_btn = tk.Label(
            button_frame, text='Сохранить', font=FONT_BOLD,
            bg=COLOR_PINK, fg=COLOR_TEXT, width=12,
            padx=5, pady=5, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        save_btn.bind('<Button-1>', lambda e: self._save())
        
        cancel_btn = tk.Label(
            button_frame, text='Отмена', font=FONT_NORMAL,
            bg=COLOR_PINK_DARK, fg=COLOR_TEXT, width=12,
            padx=5, pady=5, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        cancel_btn.bind('<Button-1>', lambda e: self.window.destroy())
    
    def _load_customer(self):
        customer = get_customer(self.customer_id)
        if customer is None:
            messagebox.showerror('Ошибка', f'Клиент id={self.customer_id} не найден')
            self.window.destroy()
            return
        
        self.name_entry.insert(0, customer.name)
        if customer.phone:
            self.phone_entry.insert(0, customer.phone)
        if customer.address:
            self.address_entry.insert(0, customer.address)
    
    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning('Ошибка', 'Введите имя клиента')
            return
        
        phone = self.phone_entry.get().strip() or None
        address = self.address_entry.get().strip() or None
        
        try:
            if self.customer_id is None:
                add_customer(name, phone, address)
                log.info(f'Создан клиент: {name}')
            else:
                update_customer(
                    self.customer_id,
                    name=name,
                    phone=phone,
                    address=address
                )
                log.info(f'Обновлён клиент id={self.customer_id}')
        except Exception as e:
            messagebox.showerror('Ошибка сохранения', str(e))
            return
        
        if self.on_save:
            self.on_save()
        
        self.window.destroy()


# ============================================================
# Окно отчётов (с выбором периода)
# ============================================================

class ReportWindow:
    """Окно с отчётами."""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title('Отчёты')
        self.window.geometry('650x600')
        self.window.configure(bg=COLOR_BG)
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        title = tk.Label(
            self.window,
            text='Отчёты',
            font=(FONT, 16, 'bold'),
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            pady=10
        )
        title.pack()
        
        # ===== Панель выбора периода =====
        period_frame = tk.Frame(self.window, bg=COLOR_BG)
        period_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            period_frame, text='Период для выручки:',
            font=FONT_NORMAL, bg=COLOR_BG, fg=COLOR_TEXT
        ).pack(side=tk.LEFT)
        
        self.period_var = tk.StringVar(value='месяц')
        self.period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.period_var,
            values=['день', 'неделя', 'месяц'],
            state='readonly',
            width=12,
            font=FONT_NORMAL,
            style='Custom.TCombobox'
        )
        self.period_combo.pack(side=tk.LEFT, padx=5)
        self.period_combo.bind('<<ComboboxSelected>>', lambda e: self._fill_report())
        
        # ===== Текст отчёта =====
        text_frame = tk.Frame(self.window, padx=10, pady=5, bg=COLOR_BG)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=FONT_MONO,
            bg=COLOR_WHITE,
            fg=COLOR_TEXT,
            padx=10,
            pady=10,
            relief=tk.SUNKEN,
            bd=2
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        
        # ===== Кнопки =====
        refresh_btn = tk.Label(
            self.window, text='Обновить', font=FONT_NORMAL,
            bg=COLOR_PINK, fg=COLOR_TEXT, width=20,
            padx=5, pady=5, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        refresh_btn.pack(pady=5)
        refresh_btn.bind('<Button-1>', lambda e: self._fill_report())
        
        close_btn = tk.Label(
            self.window, text='Закрыть', font=FONT_NORMAL,
            bg=COLOR_PINK_DARK, fg=COLOR_TEXT, width=20,
            padx=5, pady=5, relief=tk.RAISED, bd=2, cursor='hand2'
        )
        close_btn.pack(pady=5)
        close_btn.bind('<Button-1>', lambda e: self.window.destroy())
        
        self._fill_report()
    
    def _fill_report(self):
        self.text.delete('1.0', tk.END)
        
        # ===== 1. Заказы по статусам =====
        self.text.insert(tk.END, '=' * 50 + '\n')
        self.text.insert(tk.END, '  ЗАКАЗЫ ПО СТАТУСАМ\n')
        self.text.insert(tk.END, '=' * 50 + '\n\n')
        
        for status, count in report_by_status():
            self.text.insert(tk.END, f'  {status:<20} : {count}\n')
        
        # ===== 2. Топ-3 клиента =====
        self.text.insert(tk.END, '\n' + '=' * 50 + '\n')
        self.text.insert(tk.END, '  ТОП-3 КЛИЕНТА ПО СУММЕ\n')
        self.text.insert(tk.END, '=' * 50 + '\n\n')
        
        for i, (name, total, count) in enumerate(report_top_customers(3), 1):
            self.text.insert(tk.END, f'  {i}. {name:<25} {total:>10.2f} руб. ({count} заказ.)\n')
        
        # ===== 3. Выручка за период =====
        period = self.period_var.get()
        today = date.today()
        
        if period == 'день':
            start = today
            label = 'за день'
        elif period == 'неделя':
            start = today - timedelta(days=7)
            label = 'за неделю'
        else:
            start = today - timedelta(days=30)
            label = 'за месяц'
        
        revenue = report_revenue(start.isoformat(), today.isoformat())
        
        self.text.insert(tk.END, '\n' + '=' * 50 + '\n')
        self.text.insert(tk.END, f'  ВЫРУЧКА {label.upper()}\n')
        self.text.insert(tk.END, '=' * 50 + '\n\n')
        self.text.insert(tk.END, f'  {start.isoformat()} — {today.isoformat()}\n')
        self.text.insert(tk.END, f'  Итого: {revenue:.2f} руб.\n')


# ============================================================
# Точка входа
# ============================================================

def main():
    root = tk.Tk()
    app = DeliveryApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
