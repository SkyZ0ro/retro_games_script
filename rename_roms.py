import os
import re

# Список языков/регионов для поиска в квадратных скобках
LANG_CODES = [
    'RUS', 'ENG', 'JAP', 'USA', 'EUR', 'FRA', 'GER', 'SPA', 'ITA', 'CHN', 'KOR', 'BRA', 'POL', 'TUR',
    'HUN', 'SWE', 'FIN', 'NED', 'POR', 'GRE', 'CZE', 'DAN', 'NOR', 'SLO', 'SUI',
    'Rus', 'Eng', 'Jap', 'Usa', 'Eur', 'Fra', 'Ger', 'Spa', 'Ita', 'Chn', 'Kor', 'Bra', 'Pol', 'Tur',
    'Hun', 'Swe', 'Fin', 'Ned', 'Por', 'Gre', 'Cze', 'Dan', 'Nor', 'Slo', 'Sui'
]
# Список стран/регионов для поиска в круглых скобках
REGION_CODES = [
    'Europe', 'USA', 'Japan', 'Russia', 'Germany', 'France', 'Spain', 'Italy', 'England', 'World',
    'Korea', 'China', 'Brazil', 'Poland', 'Turkey', 'Hungary', 'Sweden', 'Finland', 'Netherlands',
    'Portugal', 'Greece', 'Czech', 'Denmark', 'Norway', 'Slovakia', 'Switzerland', 'Australia', 'Canada',
    'Mexico', 'Asia', 'Hong Kong', 'Taiwan', 'Argentina', 'Chile', 'India', 'Israel',
    'RUS', 'ENG', 'JAP', 'USA', 'EUR', 'FRA', 'GER', 'SPA', 'ITA', 'CHN', 'KOR', 'BRA', 'POL', 'TUR',
    'HUN', 'SWE', 'FIN', 'NED', 'POR', 'GRE', 'CZE', 'DAN', 'NOR', 'SLO', 'SUI',
    'Rus', 'Eng', 'Jap', 'Usa', 'Eur', 'Fra', 'Ger', 'Spa', 'Ita', 'Chn', 'Kor', 'Bra', 'Pol', 'Tur',
    'Hun', 'Swe', 'Fin', 'Ned', 'Por', 'Gre', 'Cze', 'Dan', 'Nor', 'Slo', 'Sui'
]

# Регулярка для поиска языков/регионов в квадратных скобках
LANG_RE = re.compile(r'\[([^\]]*(' + '|'.join(LANG_CODES) + r')[^\]]*)\]', re.IGNORECASE)
# Регулярка для поиска всех квадратных скобок
ALL_SQUARE_RE = re.compile(r'\[[^\]]*\]')
# Регулярка для поиска всех круглых скобок с содержимым
ROUND_RE = re.compile(r'\([^\)]*\)')

# Символы и слова для очистки
CLEANUP_RE = re.compile(r'^[\s\-_,.!+]+|[\s\-_,.!+]+$')
MULTISPACE_RE = re.compile(r'\s{2,}')
# Удалять " - ", " _ ", " + ", ", " перед скобками
BEFORE_PARENS_RE = re.compile(r'[\s\-_,.!+]+(?=\()')
# Регулярка для поиска PSX-кодов в квадратных скобках
PSX_CODE_RE = re.compile(r'\[(SLUS|SLES|SLPS|SCUS|SCES|SCPS|PBPX|VIBF)-\d{5}\]', re.IGNORECASE)

# Рекурсивный обход
for root, dirs, files in os.walk('Roms'):
    for fname in files:
        # Пропускаем скрытые и системные файлы
        if fname.startswith('.'):
            continue
        old_path = os.path.join(root, fname)
        name, ext = os.path.splitext(fname)

        # Проверяем, в папке psx ли файл
        is_psx = '/psx/' in old_path.replace('\\', '/').lower() or old_path.replace('\\', '/').lower().endswith('/psx')
        if is_psx:
            # Удаляем только PSX-коды в квадратных скобках
            name_psx = PSX_CODE_RE.sub('', name)
            # Остальные квадратные скобки оставляем
            name_wo_square = name_psx
        else:
            # Для остальных платформ удаляем все квадратные скобки
            name_wo_square = ALL_SQUARE_RE.sub('', name)
        # Очищаем лишние символы перед скобками
        name_wo_square = BEFORE_PARENS_RE.sub('', name_wo_square)
        # 1. Извлекаем языки/регионы из квадратных скобок
        langs = []
        for match in LANG_RE.finditer(name):
            # Берём только коды, разделяем по +, запятая или пробел
            codes = re.findall(r'(' + '|'.join(LANG_CODES) + r')', match.group(1), re.IGNORECASE)
            for code in codes:
                code_up = code.upper()
                if code_up not in langs:
                    langs.append(code_up)
        # 2. Оставляем только название и круглые скобки
        #    (название до первой скобки + все круглые скобки)
        # Название до первой скобки
        m = re.search(r'([^(]+)', name_wo_square)
        if m:
            base = m.group(1)
        else:
            base = name_wo_square
        # Очищаем от лишних символов в начале/конце
        base = CLEANUP_RE.sub('', base)
        # Все круглые скобки
        parens_all = [s.group(0) for s in ROUND_RE.finditer(name_wo_square)]
        # Оставляем только одну скобку с регионом/страной
        region_paren = None
        for p in parens_all:
            for region in REGION_CODES:
                if region.lower() in p.lower():
                    region_paren = p
                    break
            if region_paren:
                break
        parens = []
        if region_paren:
            parens.append(region_paren)
        # Добавляем языки/регионы из квадратных скобок, если есть
        if langs:
            parens.append('(' + ', '.join(langs) + ')')
        # Собираем новое имя
        new_name = base
        if parens:
            new_name += ' ' + ' '.join(parens)
        new_name = MULTISPACE_RE.sub(' ', new_name).strip() + ext
        new_path = os.path.join(root, new_name)
        # Отладочная информация
        print(f"Исходное имя: {fname}")
        print(f"Извлечённые языки: {langs}")
        print(f"Найдена региональная скобка: {region_paren}")
        print(f"Новое имя: {new_name}\n")
        # Переименовываем, если имя изменилось
        if new_path != old_path:
            print(f'Rename: {old_path} -> {new_path}')
            os.rename(old_path, new_path) 