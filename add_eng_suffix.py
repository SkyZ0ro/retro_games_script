#!/usr/bin/env python3
"""
Скрипт для добавления суффикса (USA) к именам файлов
"""

import os
import re
import argparse

def add_eng_suffix(filename):
    """Добавляет (USA) перед расширением файла, если его нет в имени"""
    name, ext = os.path.splitext(filename)
    
    # Проверяем наличие языковых меток (ENG, RUS, JPN и т.д.)
    if re.search(r'\([A-Z]{2,4}\)', name):
        return filename
    
    # Добавляем (ENG) перед расширением
    return f"{name} (USA){ext}"

def process_directory(root_dir, dry_run=True):
    """Обрабатывает файлы в директории"""
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            original_path = os.path.join(dirpath, filename)
            new_name = add_eng_suffix(filename)
            
            if filename != new_name:
                new_path = os.path.join(dirpath, new_name)
                if dry_run:
                    print(f"[DRY RUN] Переименован: {filename} -> {new_name}")
                else:
                    try:
                        os.rename(original_path, new_path)
                        print(f"Переименован: {filename} -> {new_name}")
                    except Exception as e:
                        print(f"Ошибка переименования {filename}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Добавление (USA) к именам файлов')
    parser.add_argument('path', nargs='?', default='.', help='Путь к обрабатываемой директории')
    parser.add_argument('--apply', action='store_true', help='Применить изменения')
    args = parser.parse_args()
    
    print(f"Обработка директории: {os.path.abspath(args.path)}")
    process_directory(args.path, dry_run=not args.apply)
    
    print("\nОперация завершена!")
    print(f"Режим: {'Dry run' if not args.apply else 'Реальный запуск'}")

if __name__ == "__main__":
    main()