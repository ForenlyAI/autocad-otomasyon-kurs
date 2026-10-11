"""Hafta 2 · Öznitelikli blok ve metraj: masaya kod, kişi, malzeme ve birim fiyat yaz; çizimden malzeme listesi çıkar.

AutoCAD'deki ATTDEF + ATTEXT/DATAEXTRACTION işinin Python karşılığı. (AutoCAD Web'de ATTDEF ve DATAEXTRACTION yok;
11.10.2026 yoklaması.) Fiyatlar ÖRNEK'tir.
"""
import csv
import ezdxf
from openpyxl import Workbook
from ortak import CIKTI, MASA, MASALAR, SANDALYE_YER, olc, png
from h1_katman import STANDART

OZ = [("KOD", "Masa kodu"), ("KISI", "Kişi sayısı"), ("MALZEME", "Malzeme"), ("FIYAT", "Birim fiyat (TL)")]
DEGER = [("M-01", "4", "akasya", "6500"), ("M-02", "4", "akasya", "6500"), ("M-03", "4", "ceviz", "7800"), ("M-04", "2", "ceviz", "5200")]
SANDALYE_FIYAT = 2100


def oznitelikli_blok(doc):
    b = doc.blocks.new("MASA_OZ"); h = MASA / 2
    b.add_lwpolyline([(-h, -h), (h, -h), (h, h), (-h, h)], close=True)
    for i, (etiket, istem) in enumerate(OZ):
        b.add_attdef(etiket, insert=(-h + 40, h - 140 - i * 160), text="",
                     dxfattribs={"height": 110, "prompt": istem, "layer": "A-ANNO-TEXT", "invisible": 1 if etiket == "FIYAT" else 0})


# foi bağı: insansı robot (G1) tezgâhtan masalara çay götürür. Yol ve istasyon ÖRNEK; robot gövde genişliği 450 mm varsayıldı.
ISTASYON = (7000, 5400)          # şarj istasyonu merkezi (tezgâhın kuzeyi)
ROBOT_YOLU = [(5900, 3000), (3000, 3000)]   # tezgâh önü → iki masa sırasının arası (dört masaya da buradan servis)


def robot(doc):
    b = doc.blocks.new("ROBOT_ISTASYON")
    b.add_lwpolyline([(-300, -250), (300, -250), (300, 250), (-300, 250)], close=True)
    b.add_circle((0, 0), 150)
    msp = doc.modelspace()
    msp.add_blockref("ROBOT_ISTASYON", ISTASYON, dxfattribs={"layer": "A-EQPM-ROBT"})
    msp.add_lwpolyline(ROBOT_YOLU, dxfattribs={"layer": "A-EQPM-PATH", "const_width": 40})


def main():
    doc = ezdxf.readfile(CIKTI / "kafe_standart.dxf")
    msp = doc.modelspace()
    oznitelikli_blok(doc)
    for e in msp.query('INSERT[name=="MASA"]'):
        msp.delete_entity(e)
    for (x, y), d in zip(MASALAR, DEGER):
        ref = msp.add_blockref("MASA_OZ", (x, y), dxfattribs={"layer": "A-FURN"})
        ref.add_auto_attribs(dict(zip([o[0] for o in OZ], d)))
    # M-04 iki kişilik: iki sandalyesi kaldırılır
    x4, y4 = MASALAR[3]
    for e in msp.query('INSERT[name=="SANDALYE"]'):
        if abs(e.dxf.insert.x - x4) < 1 and 1 < abs(e.dxf.insert.y - y4) < 700:
            msp.delete_entity(e)
    robot(doc)
    doc.saveas(CIKTI / "kafe_oznitelik.dxf")
    png(doc, "kafe_oznitelik", "Öznitelikli masa bloğu: kod, kişi, malzeme")

    # metraj: çizimden okunur (çizim tek doğru kaynak)
    doc = ezdxf.readfile(CIKTI / "kafe_oznitelik.dxf"); msp = doc.modelspace()
    satir = []
    for ref in msp.query('INSERT[name=="MASA_OZ"]'):
        a = {at.dxf.tag: at.dxf.text for at in ref.attribs}
        satir.append((a["KOD"], int(a["KISI"]), a["MALZEME"], int(a["FIYAT"]), round(ref.dxf.insert.x), round(ref.dxf.insert.y)))
    satir.sort()
    n_sandalye = len(msp.query('INSERT[name=="SANDALYE"]'))
    toplam_masa = sum(s[3] for s in satir); toplam = toplam_masa + n_sandalye * SANDALYE_FIYAT
    with open(CIKTI / "metraj.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["kod", "kişi", "malzeme", "birim fiyat TL", "x mm", "y mm"]); w.writerows(satir)
    wb = Workbook(); ws = wb.active; ws.title = "Metraj"
    ws.append(["Kod", "Kişi", "Malzeme", "Birim fiyat (TL)", "X (mm)", "Y (mm)"])
    for s in satir: ws.append(list(s))
    ws.append([]); ws.append(["Sandalye", n_sandalye, "", SANDALYE_FIYAT * n_sandalye])
    ws.append(["TOPLAM", sum(s[1] for s in satir), "", toplam])
    wb.save(CIKTI / "metraj.xlsx")
    olc(h2_masa=len(satir), h2_kisi=sum(s[1] for s in satir), h2_sandalye=n_sandalye, h2_masa_tl=toplam_masa,
        h2_sandalye_tl=n_sandalye * SANDALYE_FIYAT, h2_toplam_tl=toplam, h2_satirlar=satir,
        h2_kisi_sandalye_uyumu=sum(s[1] for s in satir) == n_sandalye)
    for s in satir: print(*s, sep=" · ")
    print("kişi", sum(s[1] for s in satir), "sandalye", n_sandalye, "toplam TL", toplam)


if __name__ == "__main__":
    main()
