import qrcode
import pandas as pd
import csv
import uuid
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

def generate_uuids(num_codes):
    """Generate a list of UUIDs in the specified format."""
    uuids = set()
    while len(uuids) < num_codes:
        uuids.add(f"{uuid.uuid4().hex[:8].upper()}-ECHO-01")
    return list(uuids)

def export_uuids_to_csv(NoOfUuids):
    """Export the generated UUIDs to a CSV file."""
    uuids = [f"{uuid.uuid4().hex[:8].upper()}-ECHO-01" for _ in range(NoOfUuids)]
    output_file = "codes.csv"
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['code'])  # Write header
        for code in uuids:
            writer.writerow([code])
    return output_file

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
    
    total_codes = len(codes)
    codes_per_page = codes_per_row * codes_per_col
    
    for page_num in range((total_codes + codes_per_page - 1) // codes_per_page):
        if page_num > 0:
            c.showPage()  # Start a new page
        
        # Process codes for this page
        start_index = page_num * codes_per_page
        end_index = min(start_index + codes_per_page, total_codes)
        
        for i, code in enumerate(codes[start_index:end_index]):
            # Calculate row and column within this page
            row = i // codes_per_row
            col = i % codes_per_row
            
            # Calculate position
            x = margin + col * x_spacing + (x_spacing - qr_size) / 2
            y = page_height - margin - row * y_spacing - (y_spacing - qr_size) / 2
            
            # Generate and save QR code image temporarily
            qr_img = generate_qr_code(code)
            temp_qr_path = f"temp_qr_{start_index + i}.png"
            qr_img.save(temp_qr_path)
            
            # Draw QR code image on canvas
            c.drawImage(temp_qr_path, x, y - qr_size, qr_size, qr_size)
            
            # Draw the code text below the QR code
            c.setFont("Helvetica", 10)
            text_width = c.stringWidth(code, "Helvetica", 10)
            c.drawString(x + (qr_size - text_width) / 2, y - qr_size - 10, code)
            
            # Remove the temporary QR code image
            os.remove(temp_qr_path)
    
    # Save PDF
    c.save()

def main():
    generateCodes = True
    if generateCodes:
        export_uuids_to_csv(1000)
    
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
