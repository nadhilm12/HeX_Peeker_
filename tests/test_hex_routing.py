# tests/test_hex_routing_public.py
import io, os, tempfile
from core.hex_core import iter_hex_bytes_from_stream, smart_parse_to_temp

def test_iter_hex_pure_even():
    s = io.StringIO("A1B2C3")
    assert list(iter_hex_bytes_from_stream(s)) == [0xA1, 0xB2, 0xC3]

def test_iter_hex_pure_odd_raises():
    s = io.StringIO("A1B2C")
    try:
        list(iter_hex_bytes_from_stream(s))
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "odd length" in str(e) and "line 1" in str(e)

def test_iter_hex_mixed_regex():
    # Use raw string / escaped backslash so the literal "\xCD" is present in the text
    s = io.StringIO(r"foo 0xAB bar \xCD baz EF end")
    assert list(iter_hex_bytes_from_stream(s)) == [0xAB, 0xCD, 0xEF]

def test_smart_parse_routing_binary_copy_bin():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "x.bin")
        original_content = b"\x00\x11\x22\x33"
        with open(src_path, "wb") as f:
            f.write(original_content)

        dst_name = "tmp-out.bin"
        out_path = smart_parse_to_temp(src_path, dst_name)
        with open(out_path, "rb") as f:
            assert f.read() == original_content

def test_smart_parse_routing_binary_copy_png():
    # Unknown extension should still be accepted (fallback raw-binary route)
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "image.png")
        original_content = b"\x89PNG\r\n\x1a\n\x00\x01\x02\x03"
        with open(src_path, "wb") as f:
            f.write(original_content)

        dst_name = "tmp-out2.bin"
        out_path = smart_parse_to_temp(src_path, dst_name)
        with open(out_path, "rb") as f:
            assert f.read() == original_content
