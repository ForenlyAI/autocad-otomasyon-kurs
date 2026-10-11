"""Hafta 3 · Dış referans ve revizyon: mimari plan ayrı dosya, mobilya onu dış referans (XREF) olarak bağlar;
iki revizyon arasındaki fark Python ile bulunur ve renkle işaretlenir.

AutoCAD Web'de XREF paleti ve TRACE (revizyon notu) var; CLASSICXREF, -XREF ve DWGCOMPARE yok (11.10.2026 yoklaması).
Revizyon (ÖRNEK): M-03 masa takımı 600 mm kuzeye taşındı, M-04'ün bir sandalyesi kaldırıldı, kapı 900'den 1000 mm'ye genişledi.
"""
import ezdxf
from ezdxf.math import Vec3
from ortak import LAB, CIKTI, olc, png


def ayir():
    """kafe_oznitelik.dxf → kafe_mimari.dxf (duvar + kapı, DXF karşılığı) ve kafe_mobilya.dxf (mobilya + kafe_mimari.dwg dış referansı)."""
    kaynak = ezdxf.readfile(CIKTI / "kafe_oznitelik.dxf")
    mim = ezdxf.readfile(CIKTI / "kafe_oznitelik.dxf")
    for e in list(mim.modelspace()):
        if e.dxf.layer not in ("A-WALL", "A-DOOR"):
            mim.modelspace().delete_entity(e)
    mim.saveas(CIKTI / "kafe_mimari.dxf")
    mob = kaynak
    for e in list(mob.modelspace()):
        if e.dxf.layer in ("A-WALL", "A-DOOR"):
            mob.modelspace().delete_entity(e)
    # AutoCAD dış referans olarak yalnız DWG bağlar (DXF bağlanmaz, AutoCAD Web'de 11.10.2026 denendi). ezdxf DWG yazamaz:
    # mimari DWG önceki kursta AutoCAD'de çizilip kaydedildi (ders-4.2-kafe-plani.dwg → kafe_mimari.dwg). Alternatif: ODA File Converter.
    mob.add_xref_def("kafe_mimari.dwg", "MIMARI")       # göreli yol: iki dosya aynı klasörde
    mob.modelspace().add_blockref("MIMARI", (0, 0), dxfattribs={"layer": "0"})
    mob.saveas(CIKTI / "kafe_mobilya.dxf")
    import shutil
    if (LAB / "kafe_mimari.dwg").exists():   # dış referansın DWG'si mobilya dosyasının yanında olmalı
        shutil.copy(LAB / "kafe_mimari.dwg", CIKTI / "kafe_mimari.dwg")
    return len(mim.modelspace()), len(mob.modelspace())


def revizyon():
    doc = ezdxf.readfile(CIKTI / "kafe_oznitelik.dxf"); msp = doc.modelspace()
    for ref in msp.query('INSERT[name=="MASA_OZ"]'):
        if ref.get_attrib_text("KOD") == "M-03":   # M-03 takımı (masa + 4 sandalye) 600 mm kuzeye
            x3, y3 = ref.dxf.insert.x, ref.dxf.insert.y
            ref.translate(0, 600, 0)
    for e in msp.query('INSERT[name=="SANDALYE"]'):
        if abs(e.dxf.insert.x - x3) < 700 and abs(e.dxf.insert.y - y3) < 700:
            e.translate(0, 600, 0)
    for e in msp.query('INSERT[name=="SANDALYE"]'):
        p = e.dxf.insert
        if abs(p.x - 4850) < 1 and abs(p.y - 4300) < 1:   # M-04'ün doğu sandalyesi
            msp.delete_entity(e); break
    for e in msp.query('ARC LINE[layer=="A-DOOR"]'):
        if e.dxftype() == "ARC":
            e.dxf.radius = 1000
        else:
            e.dxf.end = Vec3(e.dxf.end.x, 1000, 0)
    for pl in msp.query('LWPOLYLINE[layer=="A-WALL"]'):
        pts = [list(p) for p in pl.get_points("xy")]
        pts[-1][0] += 100                                   # kapı boşluğunun doğu ucu 100 mm kayar
        pl.set_points([tuple(p) for p in pts], format="xy")
    for e in msp.query('LINE[layer=="A-WALL"]'):
        if e.dxf.start.x > 4400:
            e.dxf.start = Vec3(e.dxf.start.x + 100, e.dxf.start.y, 0); e.dxf.end = Vec3(e.dxf.end.x + 100, e.dxf.end.y, 0)
    # kapı yayı ve kanadı doğu ucundan ölçülmez; kanat menteşede kalır (3550)
    doc.saveas(CIKTI / "kafe_rev2.dxf")


def imza(e):
    t = e.dxftype(); L = e.dxf.layer
    if t == "INSERT":
        p = e.dxf.insert; ek = e.get_attrib_text("KOD") if e.attribs else ""
        return (t, L, e.dxf.name, ek, round(p.x), round(p.y), round(e.dxf.rotation))
    if t == "LINE":
        return (t, L, *(round(v) for v in (*e.dxf.start.vec2, *e.dxf.end.vec2)))
    if t == "ARC":
        return (t, L, round(e.dxf.center.x), round(e.dxf.center.y), round(e.dxf.radius))
    if t == "LWPOLYLINE":
        return (t, L, tuple((round(x), round(y)) for x, y in e.get_points("xy")))
    if t in ("TEXT", "MTEXT"):
        return (t, L, e.plain_text() if t == "MTEXT" else e.dxf.text)
    return (t, L, e.dxf.handle)


def fark(a, b):
    A = {imza(e): e for e in ezdxf.readfile(a).modelspace()}
    B_doc = ezdxf.readfile(b); B = {imza(e): e for e in B_doc.modelspace()}
    silinen = [k for k in A if k not in B]; eklenen = [k for k in B if k not in A]
    return silinen, eklenen, B_doc


def isaretle(silinen, eklenen, doc):
    """Revizyon çizimine iki katman ekler: eklenen/değişen yeşil, silinen kırmızı bulut (dikdörtgen)."""
    doc.layers.add("Z-REV-EKLENEN", color=3); doc.layers.add("Z-REV-SILINEN", color=1)
    msp = doc.modelspace()
    def kutu(x, y, r, katman):
        msp.add_lwpolyline([(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)], close=True,
                           dxfattribs={"layer": katman, "const_width": 30})
    for k in eklenen:
        if k[0] == "INSERT" and k[2] == "MASA_OZ": kutu(k[4], k[5], 1000, "Z-REV-EKLENEN")
        elif k[0] == "ARC": kutu(k[2] + k[4] / 2, k[3] + k[4] / 2, k[4] * 0.7, "Z-REV-EKLENEN")
    yeni_yer = {(k[4], k[5]) for k in eklenen if k[0] == "INSERT"}
    for k in silinen:   # taşınan takımın eski yerleri değil, yalnız gerçekten kaldırılan sandalye
        if k[0] == "INSERT" and k[2] == "SANDALYE" and (k[4], k[5] + 600) not in yeni_yer:
            kutu(k[4], k[5], 320, "Z-REV-SILINEN")
    doc.saveas(CIKTI / "kafe_rev2_fark.dxf")


# Robot koridoru denetimi (foi): yol çizgisinden her engele (masa, sandalye, tezgâh) en az YARIM_KORIDOR mesafe.
ROBOT_GENISLIK = 450; PAY = 175                  # ÖRNEK: insansı robot gövde genişliği ~450 mm + iki yanda 175 mm → 800 mm koridor
YARIM_KORIDOR = ROBOT_GENISLIK / 2 + PAY


def koridor(dosya):
    from ezdxf import bbox
    doc = ezdxf.readfile(dosya); msp = doc.modelspace()
    yol = msp.query('LWPOLYLINE[layer=="A-EQPM-PATH"]')[0].get_points("xy")
    engeller = []
    for e in msp.query('INSERT LWPOLYLINE[layer=="A-FURN"]'):
        k = bbox.extents([e]); ad = e.get_attrib_text("KOD") if e.dxftype() == "INSERT" and e.attribs else (e.dxf.name if e.dxftype() == "INSERT" else "tezgâh")
        engeller.append((ad, k.extmin.x, k.extmin.y, k.extmax.x, k.extmax.y))
    def mesafe(px, py, r):
        _, x1, y1, x2, y2 = r
        dx = max(x1 - px, 0, px - x2); dy = max(y1 - py, 0, py - y2)
        return (dx * dx + dy * dy) ** 0.5
    en_kucuk = (1e9, None, None)
    for (ax, ay), (bx, by) in zip(yol, yol[1:]):
        n = int(max(abs(bx - ax), abs(by - ay)) // 25) + 1
        for i in range(n + 1):
            px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            for r in engeller:
                d = mesafe(px, py, r)
                if d < en_kucuk[0]: en_kucuk = (d, r[0], (round(px), round(py)))
    d, ad, nokta = en_kucuk
    return dict(en_dar_mm=int(round(2 * d)), engel=ad, nokta=[int(v) for v in nokta], gecer=bool(d >= YARIM_KORIDOR))


def main():
    n_mim, n_mob = ayir()
    revizyon()
    silinen, eklenen, doc = fark(CIKTI / "kafe_oznitelik.dxf", CIKTI / "kafe_rev2.dxf")
    isaretle(silinen, eklenen, doc)
    k1, k2 = koridor(CIKTI / "kafe_oznitelik.dxf"), koridor(CIKTI / "kafe_rev2.dxf")
    olc(h3_koridor_gerekli_mm=2 * YARIM_KORIDOR, h3_koridor_rev1=k1, h3_koridor_rev2=k2)
    print("koridor rev1", k1); print("koridor rev2", k2)
    png(doc, "kafe_rev2_fark", f"Revizyon farkı: {len(eklenen)} eklenen/değişen, {len(silinen)} silinen/eski")
    kisa = lambda k: f"{k[0]} {k[1]} {k[2] if k[0] == 'INSERT' else ''} {k[3] if k[0] == 'INSERT' else ''}".strip()
    olc(h3_mimari_nesne=n_mim, h3_mobilya_nesne=n_mob, h3_xref="MIMARI → kafe_mimari.dwg",
        h3_eklenen=len(eklenen), h3_silinen=len(silinen),
        h3_eklenen_liste=[kisa(k) for k in eklenen], h3_silinen_liste=[kisa(k) for k in silinen])
    print("mimari", n_mim, "mobilya", n_mob)
    print("EKLENEN/DEĞİŞEN:", *[kisa(k) for k in eklenen], sep="\n  ")
    print("SİLİNEN/ESKİ:", *[kisa(k) for k in silinen], sep="\n  ")


if __name__ == "__main__":
    main()
