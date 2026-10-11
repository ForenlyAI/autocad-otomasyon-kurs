"""AutoCAD + Python ile Çizim Otomasyonu — lab ortak araçları (11.10.2026).

Önceki kurs (autocad-teknik-cizim) kafe planını çizdi; bu kurs aynı planı Python (ezdxf) ile denetler, zenginleştirir
ve paftaya döker. Her sonuç AutoCAD Web'de açılıp gözle doğrulanır (gerçek ekran klibi ayrı kaydedilir).
  olc(**kw)                     : ölçümü OLCUMLER.json'a yazar (derslerdeki bütün sayılar buradan gelir)
  png(doc, ad, baslik, layout)  : DXF'i PNG'ye çizer → ekran/<ad>.png ("Gerçek koşum çıktısı" etiketiyle)
Ölçüler ÖRNEK'tir (kafe 8000 × 6000 mm, duvar 200, kapı 900; masa 800 × 800, sandalye 450 × 450).
"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, LineweightPolicy

LAB = pathlib.Path(__file__).resolve().parent
CIKTI = LAB / "cikti"; CIKTI.mkdir(exist_ok=True)
EKRAN = LAB / "ekran"; EKRAN.mkdir(exist_ok=True)
OLC = LAB / "OLCUMLER.json"
plt.rcParams.update({"font.size": 20, "font.family": "DejaVu Sans"})

ODA = dict(en=8000, boy=6000, duvar=200, kapi_x=3550, kapi=900)
MASA, SANDALYE, ARA = 800, 450, 650
MASALAR = [(1800, 1700), (1800, 4300), (4200, 1700), (4200, 4300)]
TEZGAH = (6400, 1200, 1000, 3600)
SANDALYE_YER = [(0, -ARA, 0), (0, ARA, 180), (-ARA, 0, 270), (ARA, 0, 90)]


def olc(**kw):
    d = json.loads(OLC.read_text()) if OLC.exists() else {}
    d.update(kw)
    OLC.write_text(json.dumps(d, indent=1, ensure_ascii=False))


def yeni():
    doc = ezdxf.new("R2018", setup=True, units=4)   # mm, acadiso.dwt gibi
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LWDISPLAY"] = 1
    for ad in ("Standard",):   # txt.shx Türkçe harf (ş, ğ, İ) içermez → TrueType Arial
        st = doc.styles.get(ad); st.dxf.font = "Arial.ttf"
        st.set_extended_font_data(family="Arial", italic=False, bold=False)   # AutoCAD TrueType yazıyı aile adıyla bulur (XDATA ACAD)
    doc.header["$TEXTSTYLE"] = "Standard"
    return doc


def png(doc, ad, baslik, layout=None, boyut=(16, 9)):
    fig = plt.figure(figsize=boyut, dpi=100)
    ax = fig.add_axes([0.02, 0.06, 0.96, 0.84])
    ax.set_axis_off()
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, lineweight_policy=LineweightPolicy.RELATIVE)
    lay = doc.layouts.get(layout) if layout else doc.modelspace()
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(lay, finalize=True)
    fig.suptitle(baslik, y=0.97, fontsize=24)
    fig.text(0.02, 0.015, f"Gerçek koşum çıktısı · {ad}.dxf (ezdxf {ezdxf.__version__})", fontsize=14, color="#555")
    fig.savefig(EKRAN / f"{ad}.png", facecolor="white")
    plt.close(fig)


def kafe_temel():
    """Önceki kursun kafe planı (ders 4.2), ezdxf ile: duvar, kapı, tezgâh, dört masa takımı."""
    doc = yeni()
    for ad, renk in (("DUVAR", 7), ("KAPI", 4), ("MOBILYA", 30)):
        doc.layers.add(ad, color=renk)
    m = doc.blocks.new("MASA"); h = MASA / 2
    m.add_lwpolyline([(-h, -h), (h, -h), (h, h), (-h, h)], close=True)
    s = doc.blocks.new("SANDALYE"); h = SANDALYE / 2
    s.add_lwpolyline([(-h, -h), (h, -h), (h, h), (-h, h)], close=True)
    msp = doc.modelspace()
    o = ODA; d, kx, kw = o["duvar"], o["kapi_x"], o["kapi"]
    msp.add_lwpolyline([(kx, 0), (0, 0), (0, o["boy"]), (o["en"], o["boy"]), (o["en"], 0), (kx + kw, 0)], dxfattribs={"layer": "DUVAR"})
    msp.add_lwpolyline([(kx, -d), (-d, -d), (-d, o["boy"] + d), (o["en"] + d, o["boy"] + d), (o["en"] + d, -d), (kx + kw, -d)], dxfattribs={"layer": "DUVAR"})
    msp.add_line((kx, -d), (kx, 0), dxfattribs={"layer": "DUVAR"})
    msp.add_line((kx + kw, -d), (kx + kw, 0), dxfattribs={"layer": "DUVAR"})
    msp.add_line((kx, 0), (kx, kw), dxfattribs={"layer": "KAPI"})
    msp.add_arc((kx, 0), kw, 0, 90, dxfattribs={"layer": "KAPI"})
    x, y, w, hh = TEZGAH
    msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + hh), (x, y + hh)], close=True, dxfattribs={"layer": "MOBILYA"})
    for mx, my in MASALAR:
        msp.add_blockref("MASA", (mx, my), dxfattribs={"layer": "MOBILYA"})
        for dx, dy, a in SANDALYE_YER:
            msp.add_blockref("SANDALYE", (mx + dx, my + dy), dxfattribs={"layer": "MOBILYA", "rotation": a})
    return doc
