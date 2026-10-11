"""Hafta 4 · Toplu pafta: tek bir pafta listesinden A3 yerleşimleri (layout), 1:50 görünüm penceresi, antet ve PDF seti.

AutoCAD'deki LAYOUT + MVIEW + PUBLISH işinin Python karşılığı (AutoCAD Web'de LAYOUT, MVIEW, PUBLISH yok; PLOT var).
Pafta ISO 5457 A3 yatay (420 × 297 mm), çerçeve kenar boşluğu 20 mm sol / 10 mm diğer; antet ISO 7200 alanları.
"""
import datetime
import ezdxf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, LineweightPolicy, ColorPolicy
from pypdf import PdfReader
from ortak import CIKTI, EKRAN, olc

OLCEK = 50
PAFTALAR = [   # no, ad, gösterilecek katmanlar
    ("A-101", "Kat planı", ["A-WALL", "A-DOOR", "A-ANNO-TEXT"]),
    ("A-102", "Mobilya ve robot yolu", ["A-WALL", "A-DOOR", "A-FURN", "A-ANNO-TEXT", "A-EQPM-ROBT", "A-EQPM-PATH"]),
    ("A-103", "Revizyon 2 farkı", ["A-WALL", "A-DOOR", "A-FURN", "A-EQPM-ROBT", "A-EQPM-PATH", "Z-REV-EKLENEN", "Z-REV-SILINEN"]),
]
ANTET = dict(proje="Kafe yerleşimi (ÖRNEK)", cizen="Öğrenci", kontrol="—", tarih=datetime.date(2026, 10, 11).isoformat())


def antet(psp, no, ad, sira, toplam):
    psp.add_lwpolyline([(20, 10), (410, 10), (410, 287), (20, 287)], close=True, dxfattribs={"layer": "G-ANNO-TTLB", "const_width": 0.7})
    x0, y0, en, sat = 230, 10, 180, 8
    alanlar = [("Proje", ANTET["proje"]), ("Pafta", f"{no} · {ad}"), ("Ölçek", f"1:{OLCEK}"),
               ("Çizen / Kontrol", f"{ANTET['cizen']} / {ANTET['kontrol']}"), ("Tarih", ANTET["tarih"]), ("Pafta no", f"{sira} / {toplam}")]
    psp.add_lwpolyline([(x0, y0), (x0 + en, y0), (x0 + en, y0 + sat * len(alanlar)), (x0, y0 + sat * len(alanlar))], close=True,
                       dxfattribs={"layer": "G-ANNO-TTLB"})
    for i, (k, v) in enumerate(reversed(alanlar)):
        y = y0 + i * sat
        if i: psp.add_line((x0, y), (x0 + en, y), dxfattribs={"layer": "G-ANNO-TTLB"})
        psp.add_text(k, height=2.5, dxfattribs={"layer": "G-ANNO-TTLB"}).set_placement((x0 + 2, y + 2.8))
        psp.add_text(v, height=3.2, dxfattribs={"layer": "G-ANNO-TTLB"}).set_placement((x0 + 45, y + 2.5))
    psp.add_line((x0 + 43, y0), (x0 + 43, y0 + sat * len(alanlar)), dxfattribs={"layer": "G-ANNO-TTLB"})


def main():
    doc = ezdxf.readfile(CIKTI / "kafe_rev2_fark.dxf")
    for ad in ("G-ANNO-TTLB",):
        if ad not in doc.layers: doc.layers.add(ad, color=7)
    for l in list(doc.layouts.names()):
        if l not in ("Model", "Layout1"): doc.layouts.delete(l)
    tum = [l.dxf.name for l in doc.layers]
    for sira, (no, ad, gorunur) in enumerate(PAFTALAR, 1):
        lay = doc.layouts.new(no)   # yerleşim adı kısa ve ASCII: AutoCAD sekmesi uzun adı kısaltıyor
        lay.page_setup(size=(420, 297), margins=(0, 0, 0, 0), units="mm", scale=(1, 1))
        # görünüm penceresi: kâğıtta 190 × 190 mm; 1:50 → modelde 9,5 × 9,5 m (oda 8,4 × 6,4 m sığar)
        vp = lay.add_viewport(center=(120, 150), size=(190, 190), view_center_point=(4000, 3200), view_height=190 * OLCEK)
        vp.frozen_layers = [l for l in tum if l not in gorunur and l not in ("0", "Defpoints", "G-ANNO-TTLB")]
        antet(lay, no, ad, sira, len(PAFTALAR))
    if "Layout1" in doc.layouts.names() and len(doc.layouts.names()) > 2:
        doc.layouts.delete("Layout1")
    doc.saveas(CIKTI / "kafe_paftalar.dxf")

    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, lineweight_policy=LineweightPolicy.ABSOLUTE,
                        color_policy=ColorPolicy.BLACK)   # monochrome.ctb gibi: çıktı siyah, kalınlık katmandan
    cfg_renk = Configuration(background_policy=BackgroundPolicy.WHITE, lineweight_policy=LineweightPolicy.ABSOLUTE)
    with PdfPages(CIKTI / "kafe_paftalar.pdf") as pdf:
        for no, ad, _ in PAFTALAR:
            lay = doc.layouts.get(no)
            fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
            ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
            renkli = no == "A-103"   # revizyon paftası renkli: yeşil eklenen, kırmızı silinen
            fe = Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg_renk if renkli else cfg)
            gizli = {v.dxf.handle: set(v.frozen_layers) for v in lay.viewports() if v.dxf.id > 1}
            donuk = set().union(*gizli.values())
            # ezdxf çizicisi görünüm penceresindeki dondurulmuş katmanı blok içeriğine uygulamıyor; AutoCAD'deki gibi
            # INSERT'in katmanı donuksa bloğun tamamı (öznitelikleri dahil) çizilmez
            def gizle(e, p, donuk=donuk):
                if e.dxf.hasattr("layer") and e.dxf.layer in donuk:
                    p.is_visible = False
            fe.push_property_override_function(gizle)
            fe.draw_layout(lay, finalize=False)
            ax.set_xlim(0, 420); ax.set_ylim(0, 297); ax.set_aspect("equal")
            pdf.savefig(fig);
            fig.savefig(EKRAN / f"pafta_{no}.png", dpi=110)
            plt.close(fig)
    r = PdfReader(CIKTI / "kafe_paftalar.pdf")
    boyut = [(round(float(p.mediabox.width) / 72 * 25.4), round(float(p.mediabox.height) / 72 * 25.4)) for p in r.pages]
    vps = [v for l in doc.layouts if l.name != "Model" for v in l.viewports() if v.dxf.id > 1]
    olcekler = sorted({round(v.dxf.view_height / v.dxf.height) for v in vps})
    olc(h4_pafta_sayisi=len(r.pages), h4_pdf_mm=boyut, h4_olcek=olcekler, h4_pafta_adlari=[f"{n} {a}" for n, a, _ in PAFTALAR])
    print("pdf sayfa", len(r.pages), boyut, "ölçek 1:", olcekler)


if __name__ == "__main__":
    main()
