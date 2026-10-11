"""Hafta 1 · Katman standardı: dağınık bir çizimi denetle, kurala göre düzelt, yeniden denetle.

Katman adları ABD Ulusal CAD Standardı (NCS / AIA CAD Layer Guidelines) biçiminde: <disiplin>-<ana grup>[-<alt grup>].
Bu biçim ISO 13567'nin (TS EN ISO 13567) "sorumlu taraf + eleman + sunum" alanlarına eşlenir; derste iki adlandırma
yan yana gösterilir. Renk, çizgi türü ve kalınlık nesneye değil katmana bağlıdır (ByLayer).
"""
import csv
from ortak import CIKTI, olc, png, kafe_temel

STANDART = {   # ad: (renk, kalınlık 1/100 mm, açıklama, ISO 13567 karşılığı)
    "A-WALL":      (7, 50, "duvar",            "A--WALL---E"),
    "A-DOOR":      (4, 25, "kapı",             "A--DOOR---E"),
    "A-FURN":      (30, 25, "mobilya",         "A--FURN---E"),
    "A-ANNO-TEXT": (2, 25, "yazı",             "A--ANNO---T"),
    "A-ANNO-DIMS": (3, 18, "ölçü",             "A--ANNO---D"),
    "G-ANNO-TTLB": (7, 35, "antet ve çerçeve", "G--TTLB---T"),
    "A-EQPM-ROBT": (6, 35, "robot istasyonu (foi)", "A--EQPM---E"),
    "A-EQPM-PATH": (6, 25, "robot servis yolu (foi)", "A--EQPM---P"),
}


def daginik():
    """Gerçek hayattaki gibi dağınık çizim: Türkçe/İngilizce karışık adlar, 0 katmanında nesne, elle verilmiş renk."""
    doc = kafe_temel()
    msp = doc.modelspace()
    doc.layers.get("DUVAR").rename("duvarlar")
    doc.layers.get("KAPI").rename("Layer1")
    doc.layers.get("MOBILYA").rename("mobilya yeni")
    doc.layers.add("eski_cizim", color=1)          # boş, unutulmuş katman
    t = msp.add_text("KAFE PLANI 1:50", dxfattribs={"layer": "0", "height": 250, "color": 1})   # 0 katmanı + elle renk
    t.set_placement((0, 6600))
    for e in msp.query('INSERT[name=="MASA"]')[:2]:
        e.dxf.color = 5                            # iki masaya elle mavi
    return doc


def denetle(doc):
    msp = doc.modelspace(); bulgu = []
    kullanilan = {e.dxf.layer for e in msp}
    for ly in doc.layers:
        ad = ly.dxf.name
        if ad in ("0", "Defpoints"):
            continue
        if ad not in STANDART:
            bulgu.append(("ad", ad, "standart dışı katman adı"))
        if ad not in kullanilan and ad not in STANDART:   # şablondaki standart katman boş olabilir
            bulgu.append(("bos", ad, "kullanılmayan katman"))
    for e in msp:
        if e.dxf.layer == "0":
            bulgu.append(("sifir", e.dxftype(), "nesne 0 katmanında"))
        if e.dxf.hasattr("color") and e.dxf.color not in (256,):
            bulgu.append(("renk", f"{e.dxftype()} ({e.dxf.layer})", f"renk nesneye verilmiş: {e.dxf.color}"))
    return bulgu


ESLEM = {"duvarlar": "A-WALL", "Layer1": "A-DOOR", "mobilya yeni": "A-FURN"}


def duzelt(doc):
    for eski, yeni_ad in ESLEM.items():
        doc.layers.get(eski).rename(yeni_ad)
    for ad, (renk, kalin, aciklama, iso) in STANDART.items():
        ly = doc.layers.get(ad) if ad in doc.layers else doc.layers.add(ad)
        ly.dxf.color = renk; ly.dxf.lineweight = kalin; ly.description = f"{aciklama} · ISO 13567: {iso}"
    msp = doc.modelspace()
    for e in msp:
        if e.dxf.layer == "0":
            e.dxf.layer = "A-ANNO-TEXT" if e.dxftype() in ("TEXT", "MTEXT") else "A-FURN"
        if e.dxf.hasattr("color"):
            e.dxf.color = 256
    kullanilan = {e.dxf.layer for e in msp}
    for ly in list(doc.layers):
        if ly.dxf.name not in kullanilan and ly.dxf.name not in STANDART and ly.dxf.name not in ("0", "Defpoints"):
            doc.layers.remove(ly.dxf.name)


def main():
    doc = daginik(); doc.saveas(CIKTI / "kafe_daginik.dxf")
    once = denetle(doc)
    from collections import Counter
    olc(h1_katman_sayisi=len(list(doc.layers)), h1_nesne=len(doc.modelspace()), h1_nesne_tur=dict(Counter(e.dxftype() for e in doc.modelspace())))
    with open(CIKTI / "katman_raporu_once.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([("tür", "nesne/katman", "bulgu"), *once])
    png(doc, "kafe_daginik", f"Denetim öncesi: {len(once)} bulgu")
    duzelt(doc); doc.saveas(CIKTI / "kafe_standart.dxf")
    sonra = denetle(doc)
    png(doc, "kafe_standart", f"Düzeltme sonrası: {len(sonra)} bulgu · katmanlar standart")
    tur = lambda b, t: sum(1 for x in b if x[0] == t)
    olc(h1_bulgu_once=len(once), h1_bulgu_sonra=len(sonra), h1_ad=tur(once, "ad"), h1_bos=tur(once, "bos"),
        h1_sifir=tur(once, "sifir"), h1_renk=tur(once, "renk"),
        h1_katmanlar_sonra=sorted(l.dxf.name for l in doc.layers), h1_standart=list(STANDART))
    for b in once: print(*b, sep=" · ")
    print("ÖNCE", len(once), "SONRA", len(sonra))


if __name__ == "__main__":
    main()
