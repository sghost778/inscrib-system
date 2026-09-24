# mini_pdf.py - Generador PDF puro Python (sin dependencias externas)
# Compatible con el subconjunto de API de fpdf2 usado en routes_admin.py
from datetime import datetime

PAGE_W = 210.0
PAGE_H = 297.0
MARGIN = 10.0


def _esc(s):
    if s is None:
        s = ""
    s = str(s)
    try:
        s.encode("latin-1")
        return s
    except UnicodeEncodeError:
        return s.encode("latin-1", "replace").decode("latin-1")


class MiniPDF:
    def __init__(self):
        self.pages = []
        self._ops = None
        self.x = MARGIN
        self.y = MARGIN
        self.font = "Helvetica"
        self.font_style = ""
        self.font_size = 12
        self.text_color = (0, 0, 0)
        self.fill_color = (255, 255, 255)
        self.draw_color = (0, 0, 0)
        self.add_page()

    def add_page(self):
        self._ops = []
        self.pages.append(self._ops)
        self.x = MARGIN
        self.y = MARGIN

    def set_font(self, family, style="", size=12):
        self.font = family or "Helvetica"
        self.font_style = (style or "").replace(" ", "")
        self.font_size = float(size or 12)

    def set_text_color(self, r, g=None, b=None):
        if g is None and b is None:
            self.text_color = (int(r), int(r), int(r))
        else:
            self.text_color = (int(r), int(g), int(b))

    def set_fill_color(self, r, g=None, b=None):
        if g is None and b is None:
            self.fill_color = (int(r), int(r), int(r))
        else:
            self.fill_color = (int(r), int(g), int(b))

    def set_draw_color(self, r, g=None, b=None):
        if g is None and b is None:
            self.draw_color = (int(r), int(r), int(r))
        else:
            self.draw_color = (int(r), int(g), int(b))

    def get_y(self):
        return self.y

    def get_x(self):
        return self.x

    def _ensure(self, h):
        if self.y + h > PAGE_H - MARGIN:
            self.add_page()

    def _font_key(self):
        style = self.font_style
        bold = "B" in style or "Bold" in style
        italic = "I" in style
        if bold and italic:
            return "F3"
        if bold:
            return "F2"
        if italic:
            return "F3"
        return "F1"

    def _to_pdf_y(self, y_top):
        return PAGE_H - y_top

    def line(self, x1, y1, x2, y2):
        r, g, b = self.draw_color
        y1p = self._to_pdf_y(y1)
        y2p = self._to_pdf_y(y2)
        self._ops.append(
            f"{r/255:.3f} {g/255:.3f} {b/255:.3f} RG "
            f"{x1:.2f} {y1p:.2f} m {x2:.2f} {y2p:.2f} l S"
        )

    def ln(self, h=None):
        amount = self.font_size * 0.45 if h is None else h
        self.y += amount
        self.x = MARGIN
        if self.y > PAGE_H - MARGIN:
            self.add_page()

    def cell(self, w, h=None, text="", border=0, align="L", fill=False,
             new_x=None, new_y=None, **kwargs):
        w = float(w or 0)
        h = float(h if h is not None else self.font_size * 0.4)
        if w <= 0:
            w = PAGE_W - MARGIN - self.x

        self._ensure(h)

        x, y = self.x, self.y
        r, g, b = self.text_color

        if fill:
            fr, fg, fb = self.fill_color
            y1 = self._to_pdf_y(y)
            y0 = self._to_pdf_y(y + h)
            self._ops.append(
                f"{fr/255:.3f} {fg/255:.3f} {fb/255:.3f} rg "
                f"{x:.2f} {min(y0,y1):.2f} {w:.2f} {abs(y1-y0):.2f} re f"
            )

        if border:
            dr, dg, db = self.draw_color
            y1 = self._to_pdf_y(y)
            y0 = self._to_pdf_y(y + h)
            self._ops.append(
                f"{dr/255:.3f} {dg/255:.3f} {db/255:.3f} RG 0.4 w "
                f"{x:.2f} {min(y0,y1):.2f} {w:.2f} {abs(y1-y0):.2f} re S"
            )

        content = _esc(text)
        if content:
            font_key = self._font_key()
            tw = self._text_width(content, self.font_size)
            tx = x
            if align == "C":
                tx = x + max(0, (w - tw) / 2)
            elif align == "R":
                tx = x + max(0, w - tw - 1)
            baseline = self._to_pdf_y(y + self.font_size * 0.85)
            # recorte simple si no cabe
            max_w = w - 2
            if tw > max_w and tw > 0:
                ratio = max_w / tw
                content = content[: max(1, int(len(content) * ratio))]
                tw = self._text_width(content, self.font_size)
                if align == "C":
                    tx = x + max(0, (w - tw) / 2)
                elif align == "R":
                    tx = x + max(0, w - tw - 1)
            self._ops.append(
                f"BT /{font_key} {self.font_size:.1f} Tf "
                f"{r/255:.3f} {g/255:.3f} {b/255:.3f} rg "
                f"1 0 0 1 {tx:.2f} {baseline:.2f} Tm ({content}) Tj ET"
            )

        if new_y == "NEXT":
            self.y += h
            self.x = MARGIN
            if self.y > PAGE_H - MARGIN:
                self.add_page()
        else:
            if new_x == "RIGHT" or new_x is None:
                self.x = x + w
            elif new_x == "LMARGIN":
                self.x = MARGIN

    @staticmethod
    def _text_width(text, size):
        # ancho aproximado Helvetica
        return len(text) * size * 0.5

    def multi_cell(self, w, h, text, **kwargs):
        words = str(text).split()
        line = ""
        for word in words:
            test = (line + " " + word).strip()
            if self._text_width(test, self.font_size) > w and line:
                self.cell(w, h, line, new_x="LMARGIN", new_y="NEXT")
                line = word
            else:
                line = test
        if line:
            self.cell(w, h, line, new_x="LMARGIN", new_y="NEXT")

    def output(self):
        objects = []

        def add_obj(body):
            objects.append(body)
            return len(objects)

        # 1: Catalog, 2: Pages, fonts 3-6, then pages
        font_defs = {
            "F1": ("Helvetica", "Helvetica"),
            "F2": ("Helvetica-Bold", "Helvetica-Bold"),
            "F3": ("Helvetica-Oblique", "Helvetica-Oblique"),
        }
        catalog_id = 1
        pages_id = 2
        objects.append(None)  # slot 1
        objects.append(None)  # slot 2
        font_ids = {}
        for key, (base, _) in font_defs.items():
            oid = add_obj(
                f"<< /Type /Font /Subtype /Type1 /BaseFont /{base} "
                f"/Encoding /WinAnsiEncoding >>"
            )
            font_ids[key] = oid

        page_ids = []
        content_ids = []
        res = (
            "<< /Font << "
            + " ".join(f"/{k} {v} 0 R" for k, v in font_ids.items())
            + " >> >>"
        )
        for ops in self.pages:
            stream = "\n".join(ops).encode("latin-1", "replace")
            cid = add_obj(
                f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
                + stream
                + b"\nendstream"
            )
            content_ids.append(cid)

        for cid in content_ids:
            pid = add_obj(
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {PAGE_W} {PAGE_H}] "
                f"/Contents {cid} 0 R /Resources {res} >>"
            )
            page_ids.append(pid)

        kids = " ".join(f"{pid} 0 R" for pid in page_ids)
        objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>"
        objects[catalog_id - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>"

        out = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for i, obj in enumerate(objects, start=1):
            offsets.append(len(out))
            if isinstance(obj, bytes):
                out += f"{i} 0 obj\n".encode("latin-1")
                out += obj
                out += b"\nendobj\n"
            else:
                out += f"{i} 0 obj\n{obj}\nendobj\n".encode("latin-1")

        xref_pos = len(out)
        n = len(objects) + 1
        out += f"xref\n0 {n}\n".encode("latin-1")
        out += b"0000000000 65535 f \n"
        for off in offsets[1:]:
            out += f"{off:010d} 00000 n \n".encode("latin-1")
        out += (
            f"trailer\n<< /Size {n} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n"
        ).encode("latin-1")
        return bytes(out)
