import io
import qrcode


def generate_qr_code(url: str) -> bytes:
    """
    Generate a QR code for the given URL and return it as bytes.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    return byte_arr.getvalue()