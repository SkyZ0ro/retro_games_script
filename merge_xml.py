import xml.etree.ElementTree as ET
import os

# Функция для чтения XML-файла
def read_xml_file(file_path):
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        return None
    except ET.ParseError:
        print(f"Ошибка парсинга файла {file_path}.")
        return None

# Функция для объединения XML-файлов
def merge_xml_files(file1_path, file2_path, output_path):
    # Чтение обоих файлов
    root1 = read_xml_file(file1_path)
    root2 = read_xml_file(file2_path)
    
    if root1 is None or root2 is None:
        print("Не удалось загрузить один из XML-файлов.")
        return
    
    # Создание нового корневого элемента
    merged_root = ET.Element("gameList")
    
    # Словарь для хранения уникальных игр (ключ — путь файла <path>)
    games_dict = {}
    
    # Функция для добавления игр в словарь
    def add_games(root):
        for game in root.findall("game"):
            path = game.find("path")
            if path is not None and path.text:
                games_dict[path.text] = game
    
    # Добавление игр из обоих файлов
    add_games(root1)
    add_games(root2)
    
    # Добавление всех уникальных игр в новый корневой элемент
    for game in games_dict.values():
        merged_root.append(game)
    
    # Создание нового дерева и сохранение в файл
    merged_tree = ET.ElementTree(merged_root)
    merged_tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"Объединённый файл сохранён как {output_path}")

# Пути к файлам
file1_path = "gamelist_.xml"
file2_path = "gamelist.xml"
output_path = "gamelist___.xml"

# Выполнение объединения
merge_xml_files(file1_path, file2_path, output_path)