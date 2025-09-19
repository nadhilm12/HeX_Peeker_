# helpers/search_worker.py

import re
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class SearchWorker(QObject):
    """
    Worker untuk melakukan pencarian sekuens byte atau teks secara asinkron.
    """
    progress = pyqtSignal(int)
    found_offsets = pyqtSignal(list)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    @pyqtSlot(bytes, object, str)
    def run(self, data: bytes, query, mode: str):
        """
        Jalankan proses pencarian di thread ini.
        """
        try:
            search_bytes = b''
            if mode == 'Teks (ASCII)':
                search_bytes = query.encode('ascii', errors='ignore')
            elif mode == 'Hexadecimal':
                # Hapus spasi dan karakter non-hex, lalu konversi
                clean_query = re.sub(r'[^0-9a-fA-F]', '', query)
                if len(clean_query) % 2 != 0:
                    self.error.emit("String Hex harus memiliki panjang genap.")
                    return
                search_bytes = bytes.fromhex(clean_query)
            
            if not search_bytes:
                self.found_offsets.emit([])
                self.finished.emit()
                return

            offsets = []
            current_pos = 0
            total_len = len(data)
            
            while True:
                pos = data.find(search_bytes, current_pos)
                if pos == -1:
                    break
                offsets.append(pos)
                current_pos = pos + 1
                
                # Kirim progress setiap menemukan beberapa hasil agar UI tetap update
                if len(offsets) % 100 == 0:
                    self.progress.emit(int(current_pos / total_len * 100))

            self.progress.emit(100)
            self.found_offsets.emit(offsets)

        except Exception as e:
            self.error.emit(f"Error saat pencarian: {str(e)}")
        finally:
            self.finished.emit()
