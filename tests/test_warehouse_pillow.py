"""Exercise the Warehouse image callers without requiring a desktop display."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class WarehouseImageTest(unittest.TestCase):
    def test_editor_opens_and_displays_oversized_image(self):
        tkinter = ModuleType('tkinter')
        tkinter.NW = 'nw'
        tkinter.filedialog = MagicMock()
        image_tk = ModuleType('PIL.ImageTk')
        image_tk.PhotoImage = MagicMock()
        path = ROOT / 'WareHouse/ImgEditor_THUNLP_20230824142740/main.py'
        spec = importlib.util.spec_from_file_location('warehouse_editor', path)
        module = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {'tkinter': tkinter, 'PIL.ImageTk': image_tk}):
            spec.loader.exec_module(module)
            editor = module.ImageEditor.__new__(module.ImageEditor)
            editor.canvas = MagicMock()
            editor.canvas.winfo_width.return_value = 120
            editor.canvas.winfo_height.return_value = 100
            editor.undo_stack = []
            editor.redo_stack = []
            with tempfile.TemporaryDirectory() as directory:
                image = Path(directory) / 'input.png'
                Image.new('RGB', (400, 200), 'red').save(image)
                tkinter.filedialog.askopenfilename.return_value = str(image)
                editor.open_image()
                self.assertEqual(editor.current_image.size, (120, 60))
                self.assertEqual(editor.original_image.size, (400, 200))
                editor.flip_image()
                editor.adjust_brightness()
                self.assertEqual(editor.current_image.size, (120, 60))
                editor.canvas.create_image.assert_called()

    def test_gomoku_image_assets_still_decode_and_resize(self):
        directory = ROOT / 'WareHouse/Gomoku_THUNLP_20230625201030'
        names = ['black_chess_piece.png', 'white_chess_piece.png', 'background.png']
        if not any((directory / name).exists() for name in names):
            self.skipTest('Warehouse image assets are not checked in')
        for name in names:
            path = directory / name
            if path.exists():
                with self.subTest(name=name), Image.open(path) as image:
                    image.load()
                    self.assertEqual(image.resize((50, 50)).size, (50, 50))


if __name__ == '__main__':
    unittest.main()
