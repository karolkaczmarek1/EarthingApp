TRANS = {
    'en': {
        'app_title': 'Earthing Design Tool',
        'file': 'File',
        'export': 'Export Report',
        'language': 'Language',
        'tools': 'Tools',
        'select': 'Select',
        'strip': 'Strip',
        'rod': 'Rod',
        'mesh': 'Mesh',
        'plate': 'Plate',
        'properties': 'Properties',
        'simulate': 'Simulate',
        'results': 'Results',
        'resistance': 'Total Resistance',
        'gpr': 'Ground Potential Rise (GPR)',
        'grid_step': 'Grid Step (m)',
        'snap_to_grid': 'Snap to Grid',
        'width': 'Width (m)',
        'length': 'Length (m)',
        'depth': 'Depth (m)',
        'diameter': 'Diameter (m)',
        'resistivity': 'Resistivity (Ohm-m)',
        'x': 'X (m)',
        'y': 'Y (m)',
        'nx': 'Nx (conductors)',
        'ny': 'Ny (conductors)',
        'run': 'Run Simulation',
        'generating': 'Generating model...',
        'solving': 'Solving...',
        'done': 'Done.',
        'error': 'Error',
        'report_saved': 'Report saved to',
        'switch_lang': 'Polski',
        'type': 'Type',
        'delete': 'Delete',
        'clear': 'Clear All',
        'plot_surface': 'Surface Potential',
        'plot_geometry': 'Geometry 3D',
        'profile_type': 'Profile Type',
        'flat': 'Flat Strip (Tape)',
        'round': 'Round Wire',
        'radius': 'Radius (m)',
        'explode': 'Explode Mesh'
    },
    'pl': {
        'app_title': 'Narzędzie do Projektowania Uziemień',
        'file': 'Plik',
        'export': 'Eksportuj Raport',
        'language': 'Język',
        'tools': 'Narzędzia',
        'select': 'Wybierz',
        'strip': 'Bednarka (Linia)',
        'rod': 'Pręt (Szpilka)',
        'mesh': 'Siatka',
        'plate': 'Płyta',
        'properties': 'Właściwości',
        'simulate': 'Symulacja',
        'results': 'Wyniki',
        'resistance': 'Rezystancja Całkowita',
        'gpr': 'GPR (Wzrost Potencjału)',
        'grid_step': 'Krok siatki (m)',
        'snap_to_grid': 'Przyciągaj do siatki',
        'width': 'Szerokość (m)',
        'length': 'Długość (m)',
        'depth': 'Głębokość (m)',
        'diameter': 'Średnica (m)',
        'resistivity': 'Rezystywność (Ohm-m)',
        'x': 'X (m)',
        'y': 'Y (m)',
        'nx': 'Nx (przewody)',
        'ny': 'Ny (przewody)',
        'run': 'Uruchom Symulację',
        'generating': 'Generowanie modelu...',
        'solving': 'Obliczanie...',
        'done': 'Zakończono.',
        'error': 'Błąd',
        'report_saved': 'Raport zapisano w',
        'switch_lang': 'English',
        'type': 'Typ',
        'delete': 'Usuń',
        'clear': 'Wyczyść wszystko',
        'plot_surface': 'Potencjał Powierzchniowy',
        'plot_geometry': 'Geometria 3D',
        'profile_type': 'Typ Przekroju',
        'flat': 'Bednarka (Płaskownik)',
        'round': 'Drut (Okrągły)',
        'radius': 'Promień (m)',
        'explode': 'Rozbij Siatkę'
    }
}

class Translator:
    def __init__(self, lang='pl'):
        self.lang = lang

    def get(self, key):
        return TRANS.get(self.lang, {}).get(key, key)

    def set_language(self, lang):
        if lang in TRANS:
            self.lang = lang

current_translator = Translator()

def t(key):
    return current_translator.get(key)
