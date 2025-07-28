#!/usr/bin/env python3
"""
Скрипт для удаления дубликатов файлов с сохранением последней версии
Поддерживает версионность по ключевым словам: Beta, Rev, Proto
"""

import os
import re
import argparse
from collections import defaultdict
from datetime import datetime

VERSION_KEYWORDS = ['beta', 'rev', 'proto']
VERSION_PATTERN = re.compile(r'\(({})\)'.format('|'.join(VERSION_KEYWORDS)), re.IGNORECASE)

def extract_base_name(filename):
    """Извлекает базовое имя файла, удаляя ВСЕ скобочные конструкции и нормализуя пробелы"""
    # Удаляем все круглые скобки и их содержимое
    base = re.sub(r'\s*\([^)]*\)', '', filename)
    # Удаляем все квадратные скобки и их содержимое
    base = re.sub(r'\s*\[[^\]]*\]', '', base)
    # Разделяем слитные слова (camelCase и PascalCase)
    base = re.sub(r'([a-z])([A-Z])', r'\1 \2', base)
    # Заменяем множественные пробелы на один
    base = re.sub(r'\s+', ' ', base)
    # Удаляем расширение файла
    base = os.path.splitext(base)[0]
    # Удаляем пробелы в начале/конце и приводим к нижнему регистру для единообразия
    return base.strip().lower()

def is_versioned_file(filename):
    """Проверяет, содержит ли имя файла версионную метку"""
    return VERSION_PATTERN.search(filename) is not None

def process_directory(root_dir, dry_run=True):
    """Обрабатывает директорию, возвращает статистику"""
    file_groups = defaultdict(list)
    deleted_count = 0
    kept_count = 0
    
    # Сбор файлов
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            base_name = extract_base_name(filename)
            file_groups[base_name].append(file_path)
    
    # Обработка групп
    for base_name, files in file_groups.items():
        if len(files) == 1:
            kept_count += 1
            continue
            
        # Сортировка по дате изменения (последние сначала)
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        latest_file = files[0]
        
        # Для всех дубликатов удаляем все кроме последнего (независимо от версионности)
        files_to_delete = files[1:]
        
        # Удаление файлов
        for file_path in files_to_delete:
            if dry_run:
                print(f"[DRY RUN] Удалено: {file_path}")
            else:
                try:
                    os.remove(file_path)
                    print(f"Удалено: {file_path}")
                except Exception as e:
                    print(f"Ошибка удаления {file_path}: {str(e)}")
            deleted_count += 1
        
        kept_count += 1
    
    return kept_count, deleted_count

def main():
    parser = argparse.ArgumentParser(description='Удаление дубликатов файлов с сохранением последней версии')
    parser.add_argument('path', nargs='?', default='.', help='Путь к обрабатываемой директории')
    parser.add_argument('--apply', action='store_true', help='Применить изменения (без этого флага - dry run)')
    args = parser.parse_args()
    
    print(f"Обработка директории: {os.path.abspath(args.path)}")
    kept, deleted = process_directory(args.path, dry_run=not args.apply)
    
    print("\nРезультат:")
    print(f"Оставлено файлов: {kept}")
    print(f"Удалено файлов: {deleted}")
    print(f"Режим: {'Dry run' if not args.apply else 'Реальный запуск'}")

if __name__ == "__main__":
    main()