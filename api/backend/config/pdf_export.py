"""
HTML → PDF / PNG export helpers (pure Python, Windows-friendly).

Uses xhtml2pdf (ReportLab) for PDF and PyMuPDF to rasterize PDF pages for PNG.
"""

from __future__ import annotations

import io
from typing import Optional

from rest_framework.exceptions import ValidationError


def html_to_pdf_bytes(html: str) -> bytes:
    """Render HTML string to PDF bytes."""
    try:
        from xhtml2pdf import pisa
    except ImportError as exc:
        raise ValidationError(
            {
                "format": (
                    "PDF export is unavailable: install the xhtml2pdf package "
                    "(pip install xhtml2pdf)."
                )
            }
        ) from exc

    buffer = io.BytesIO()
    status = pisa.CreatePDF(
        src=html,
        dest=buffer,
        encoding="utf-8",
    )
    if status.err:
        raise ValidationError(
            {"format": "Could not render HTML to PDF. Check export HTML content."}
        )
    return buffer.getvalue()


def html_to_png_bytes(html: str, *, scale: float = 2.0) -> bytes:
    """Render HTML to PNG by generating a PDF page and rasterizing it."""
    pdf_bytes = html_to_pdf_bytes(html)
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise ValidationError(
            {
                "format": (
                    "PNG export is unavailable: install the pymupdf package "
                    "(pip install pymupdf)."
                )
            }
        ) from exc

    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
        if document.page_count < 1:
            raise ValidationError({"format": "Could not render org chart for PNG export."})
        page = document.load_page(0)
        matrix = fitz.Matrix(scale, scale)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        return pixmap.tobytes("png")
    except ValidationError:
        raise
    except Exception as exc:
        raise ValidationError(
            {"format": f"Could not convert PDF to PNG: {exc}"}
        ) from exc
    finally:
        if "document" in locals():
            document.close()


def export_html(
    html: str,
    export_format: str,
    *,
    image_base64: Optional[str] = None,
    png_filename_prefix: str = "export",
) -> dict:
    """
    Return dict with content, content_type, filename for pdf or png export.

    For PNG, uses image_base64 when provided; otherwise server-renders via PDF→PNG.
    """
    import base64

    from django.utils import timezone

    export_format = (export_format or "").lower()
    if export_format not in {"png", "pdf"}:
        raise ValidationError({"format": "Must be 'png' or 'pdf'."})

    stamp = timezone.now().strftime("%Y%m%d_%H%M%S")

    if export_format == "png" and image_base64:
        try:
            raw = image_base64
            if "," in raw:
                raw = raw.split(",", 1)[1]
            content = base64.b64decode(raw)
        except Exception as exc:
            raise ValidationError({"image_base64": "Invalid base64 image data."}) from exc
        return {
            "content": content,
            "content_type": "image/png",
            "filename": f"{png_filename_prefix}_{stamp}.png",
        }

    if export_format == "pdf":
        return {
            "content": html_to_pdf_bytes(html),
            "content_type": "application/pdf",
            "filename": f"{png_filename_prefix}_{stamp}.pdf",
        }

    return {
        "content": html_to_png_bytes(html),
        "content_type": "image/png",
        "filename": f"{png_filename_prefix}_{stamp}.png",
    }
