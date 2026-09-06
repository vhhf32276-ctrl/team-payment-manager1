from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def make_payment_pdf(payment):
    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 60, "Payment Receipt")

    pdf.setFont("Helvetica", 11)

    y = height - 110

    fields = [
        ("Company", payment["company_name"] or ""),
        ("Payment Date", payment["payment_date"] or ""),
        ("Expected Amount", f'{payment["expected"]:.2f}'),
        ("Paid Amount", f'{payment["paid"]:.2f}'),
        ("Difference", f'{payment["paid"] - payment["expected"]:.2f}'),
        ("Note", payment["note"] or ""),
    ]

    for label, value in fields:
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(50, y, label + ":")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(170, y, str(value))
        y -= 28

    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        50,
        50,
        "Software Developed by Arslan.Ak | Contact: 03200199895"
    )

    pdf.save()
    buffer.seek(0)

    return buffer
