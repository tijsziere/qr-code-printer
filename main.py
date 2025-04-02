import qrcode
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
import os

# Configurations
qr_size = 50 * mm  # Size of QR code in mm
margin = 10 * mm   # Margin around the QR code
codes_per_row = 2
codes_per_col = 4
page_width, page_height = A4

# Calculate space between QR codes
x_spacing = (page_width - 2 * margin) / codes_per_row
y_spacing = (page_height - 2 * margin) / codes_per_col

def generate_qr_code(code: str):
    """Generate QR code image from a given code."""
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(code)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    return qr_img

def generate_pdf(codes):
    """Generate a PDF with QR codes."""
    c = canvas.Canvas("qr_codes.pdf", pagesize=A4)
    
    index = 0
    for code in codes:
        # Calculate row and column
        row = index // codes_per_row
        col = index % codes_per_row
        
        # Calculate position
        x = margin + col * x_spacing + (x_spacing - qr_size) / 2
        y = page_height - margin - row * y_spacing - (y_spacing - qr_size) / 2

        # Generate and save QR code image temporarily
        qr_img = generate_qr_code(code)
        temp_qr_path = f"temp_qr_{index}.png"
        qr_img.save(temp_qr_path)

        # Draw QR code image on canvas
        c.drawImage(temp_qr_path, x, y - qr_size, qr_size, qr_size)

        # Draw the code text below the QR code
        c.setFont("Helvetica", 10)
        text_width = c.stringWidth(code, "Helvetica", 10)
        c.drawString(x + (qr_size - text_width) / 2, y - qr_size - 10, code)

        # Remove the temporary QR code image
        os.remove(temp_qr_path)

        # Move to the next position
        index += 1
        
        # If 8 QR codes are printed, add a new page
        if index % (codes_per_row * codes_per_col) == 0:
            c.showPage()
            index = 0

    # Save PDF
    c.save()

def main():
    # Read CSV file
    csv_file = "codes.csv"
    df = pd.read_csv(csv_file)

    # Check if 'code' column exists
    if 'code' not in df.columns:
        print("The CSV file must have a 'code' column.")
        return
    
    # Get list of codes
    codes = df['code'].dropna().astype(str).tolist()

    # Generate PDF with QR codes
    generate_pdf(codes)
    print("PDF file 'qr_codes.pdf' has been generated.")

if __name__ == "__main__":
    main()
