import argparse
from datetime import date, timedelta
from database import report_by_status, report_top_customers, report_revenue, get_all_orders
from data_export import export_to_json, import_from_json
from logger_config import setup_logger
log = setup_logger()

def cmd_report(args):
    period = args.period
    today = date.today()
    if period == 'day':
        start = today
    elif period == 'week':
        start = today - timedelta(days=7)
    elif period == 'month':
        start = today - timedelta(days=30)
    else:
        log.error(f'Неизвестный период: {period}')
        return
    start_str = start.isoformat()
    end_str = today.isoformat()
    log.info(f'Отчёт за период: {start_str} — {end_str}')
    print()
    print('=' * 50)
    print('  ЗАКАЗЫ ПО СТАТУСАМ')
    print('=' * 50)
    for status, count in report_by_status():
        print(f'  {status:<15} : {count}')
    print()
    print('=' * 50)
    print('  ТОП-3 КЛИЕНТА ПО СУММЕ ЗАКАЗОВ')
    print('=' * 50)
    for i, (name, total, count) in enumerate(report_top_customers(3), 1):
        print(f'  {i}. {name:<25} {total:>10.2f} руб. ({count} заказ.)')
    revenue = report_revenue(start_str, end_str)
    print()
    print('=' * 50)
    print(f'  ВЫРУЧКА ЗА ПЕРИОД ({period})')
    print('=' * 50)
    print(f'  {start_str} — {end_str}')
    print(f'  Итого: {revenue:.2f} руб.')
    print()

def cmd_export(args):
    filename = args.file
    count = export_to_json(filename)
    print(f'✅ Экспортировано {count} заказов в {filename}')

def cmd_import(args):
    filename = args.file
    count = import_from_json(filename)
    print(f'✅ Импортировано {count} заказов из {filename}')

def build_parser():
    parser = argparse.ArgumentParser(prog='main_cli.py', description='Система учёта заказов «Быстрая доставка»')
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    report_parser = subparsers.add_parser('report', help='Показать отчёты')
    report_parser.add_argument('--period', choices=['day', 'week', 'month'], default='month', help='Период для отчёта (по умолчанию: month)')
    report_parser.set_defaults(func=cmd_report)
    export_parser = subparsers.add_parser('export', help='Экспорт заказов в JSON')
    export_parser.add_argument('--file', required=True, help='Имя файла для сохранения (например, orders.json)')
    export_parser.set_defaults(func=cmd_export)
    import_parser = subparsers.add_parser('import', help='Импорт заказов из JSON')
    import_parser.add_argument('--file', required=True, help='Имя файла для загрузки')
    import_parser.set_defaults(func=cmd_import)
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    try:
        args.func(args)
    except Exception as e:
        log.error(f'Ошибка: {e}')
        print(f'❌ Ошибка: {e}')
if __name__ == '__main__':
    main()
