import os
import shutil
from collections import defaultdict
import re

# Корневые папки
ROMS_ROOT = 'Roms'
CHEATS_ROOT = 'Cheats'

# Функция для извлечения "чистого" названия (без скобок и расширения)
def clean_title(name):
    # Убираем всё в скобках и пробелы в конце
    return re.sub(r'\s*\([^)]*\)', '', os.path.splitext(name)[0]).strip()

def normalize_title(name):
    # Удалить всё в скобках (круглых и квадратных), дефисы, подчёркивания, привести к нижнему регистру, убрать лишние пробелы
    name = os.path.splitext(name)[0]
    name = re.sub(r'\[[^\]]*\]', '', name)
    name = re.sub(r'\([^)]*\)', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    name = re.sub(r'\s+', ' ', name)
    return name.strip().lower()

# Словарь: {system: [rom_name_with_ext]}
roms_by_system = defaultdict(list)  # {system: [rom_filename]}
# Словарь: {system: {clean_title: [rom_filename]}}
rom_titles_by_system = defaultdict(lambda: defaultdict(list))  # {system: {clean_title: [rom_filename]}}
rom_norm_titles_by_system = defaultdict(lambda: defaultdict(list))

# Собираем все имена ромов по системам
for sys_dir in os.listdir(ROMS_ROOT):
    sys_path = os.path.join(ROMS_ROOT, sys_dir)
    if not os.path.isdir(sys_path):
        continue
    for root, dirs, files in os.walk(sys_path):
        for fname in files:
            roms_by_system[sys_dir].append(fname)
            title = clean_title(fname)
            rom_titles_by_system[sys_dir][title].append(fname)
            norm_title = normalize_title(fname)
            rom_norm_titles_by_system[sys_dir][norm_title].append(fname)

# Для отчёта
cheats_found = defaultdict(int)
cheats_total = defaultdict(int)
cheats_created = defaultdict(int)

# Проходим по папкам Cheats
for sys_dir in os.listdir(CHEATS_ROOT):
    sys_cheat_path = os.path.join(CHEATS_ROOT, sys_dir)
    if not os.path.isdir(sys_cheat_path):
        continue
    # Получаем список всех .cht файлов
    cheat_files = [f for f in os.listdir(sys_cheat_path) if f.endswith('.cht')]
    cheats_total[sys_dir] = len(cheat_files)
    # Список файлов, которые должны остаться
    cheats_to_keep = set()
    for cheat_file in cheat_files:
        rom_name = cheat_file[:-4]
        # 1. Точное совпадение
        if rom_name in roms_by_system.get(sys_dir, []):
            cheats_found[sys_dir] += 1
            cheats_to_keep.add(cheat_file)
            continue
        # 2. По "чистому" названию
        cheat_title = clean_title(rom_name)
        roms_with_title = rom_titles_by_system[sys_dir].get(cheat_title, [])
        if roms_with_title:
            for rom in roms_with_title:
                new_cheat_name = rom + '.cht'
                new_cheat_path = os.path.join(sys_cheat_path, new_cheat_name)
                if not os.path.exists(new_cheat_path):
                    shutil.copy2(os.path.join(sys_cheat_path, cheat_file), new_cheat_path)
                    cheats_created[sys_dir] += 1
                    print(f'Создан чит: {new_cheat_name} для ROM: {rom}')
                cheats_to_keep.add(new_cheat_name)
            continue
        # 3. По нормализованному названию (без скобок, дефисов, регистра)
        cheat_norm_title = normalize_title(rom_name)
        roms_with_norm_title = rom_norm_titles_by_system[sys_dir].get(cheat_norm_title, [])
        if roms_with_norm_title:
            for rom in roms_with_norm_title:
                new_cheat_name = rom + '.cht'
                new_cheat_path = os.path.join(sys_cheat_path, new_cheat_name)
                if not os.path.exists(new_cheat_path):
                    shutil.copy2(os.path.join(sys_cheat_path, cheat_file), new_cheat_path)
                    cheats_created[sys_dir] += 1
                    print(f'Создан чит: {new_cheat_name} для ROM: {rom}')
                cheats_to_keep.add(new_cheat_name)
            continue
    # Удаляем все .cht-файлы, которые не в cheats_to_keep
    for cheat_file in cheat_files:
        if cheat_file not in cheats_to_keep:
            print(f'Удалён лишний чит: {cheat_file}')
            os.remove(os.path.join(sys_cheat_path, cheat_file))

# Выводим отчёт
print('Отчёт по найденным и созданным читам:')
for sys in sorted(set(list(cheats_total.keys()) + list(cheats_created.keys()))):
    print(f'{sys}: найдено {cheats_found[sys]}, создано {cheats_created[sys]}, всего было {cheats_total[sys]}') 