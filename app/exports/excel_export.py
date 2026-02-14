from io import BytesIO
from openpyxl import Workbook
from fastapi.responses import StreamingResponse


def export_excel(filename: str, headers: list[str], rows: list[list]):
    wb = Workbook()
    ws = wb.active

    ws.append(headers)
    for row in rows:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )