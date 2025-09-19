# ui/data_inspector.py

import struct
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QFrame

class DataInspectorPanel(QWidget):
    """
    Panel untuk menampilkan interpretasi data dari byte yang dipilih.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(250)
        self.layout = QFormLayout(self)
        self.layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.fields = {}
        
        # Buat label untuk setiap tipe data
        self._add_header("Integer (Little Endian)")
        self._add_field("Int8", "i8_le")
        self._add_field("UInt8", "u8_le")
        self._add_field("Int16", "i16_le")
        self._add_field("UInt16", "u16_le")
        self._add_field("Int32", "i32_le")
        self._add_field("UInt32", "u32_le")
        self._add_field("Int64", "i64_le")
        self._add_field("UInt64", "u64_le")

        self._add_header("Floating Point (Little Endian)")
        self._add_field("Float", "f32_le")
        self._add_field("Double", "f64_le")

        self._add_header("Integer (Big Endian)")
        self._add_field("Int16", "i16_be")
        self._add_field("UInt16", "u16_be")
        self._add_field("Int32", "i32_be")
        self._add_field("UInt32", "u32_be")
        self._add_field("Int64", "i64_be")
        self._add_field("UInt64", "u64_be")
        
    def _add_header(self, text):
        label = QLabel(f"<b>{text}</b>")
        self.layout.addRow(label)

    def _add_field(self, label_text, key):
        label = QLabel("-")
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.fields[key] = label
        self.layout.addRow(label_text, self.fields[key])

    def update_data(self, chunk: bytes):
        """Unpack byte chunk dan update semua field label."""
        if not chunk:
            for label in self.fields.values():
                label.setText("-")
            return
            
        def unpack_safe(fmt, data):
            try:
                # Pad data jika tidak cukup panjang
                padded_data = data.ljust(struct.calcsize(fmt), b'\x00')
                return str(struct.unpack(fmt, padded_data)[0])
            except (struct.error, IndexError):
                return "N/A"

        # Little Endian
        self.fields["i8_le"].setText(unpack_safe('<b', chunk[:1]))
        self.fields["u8_le"].setText(unpack_safe('<B', chunk[:1]))
        self.fields["i16_le"].setText(unpack_safe('<h', chunk[:2]))
        self.fields["u16_le"].setText(unpack_safe('<H', chunk[:2]))
        self.fields["i32_le"].setText(unpack_safe('<i', chunk[:4]))
        self.fields["u32_le"].setText(unpack_safe('<I', chunk[:4]))
        self.fields["i64_le"].setText(unpack_safe('<q', chunk[:8]))
        self.fields["u64_le"].setText(unpack_safe('<Q', chunk[:8]))
        self.fields["f32_le"].setText(unpack_safe('<f', chunk[:4]))
        self.fields["f64_le"].setText(unpack_safe('<d', chunk[:8]))
        
        # Big Endian
        self.fields["i16_be"].setText(unpack_safe('>h', chunk[:2]))
        self.fields["u16_be"].setText(unpack_safe('>H', chunk[:2]))
        self.fields["i32_be"].setText(unpack_safe('>i', chunk[:4]))
        self.fields["u32_be"].setText(unpack_safe('>I', chunk[:4]))
        self.fields["i64_be"].setText(unpack_safe('>q', chunk[:8]))
        self.fields["u64_be"].setText(unpack_safe('>Q', chunk[:8]))
