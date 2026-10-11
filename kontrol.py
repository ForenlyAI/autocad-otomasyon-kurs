"""Kendi koşumunuzu ekibin ölçtüğü sonuçla karşılaştırır.  Kullanım: python kontrol.py
Önce dört betiği sırayla koşun (README). Değer farklıysa ✗ yazar; o haftanın betiğindeki girdiyi kontrol edin."""
import json, pathlib
B = pathlib.Path(__file__).resolve().parent
siz = json.loads((B / "lab/OLCUMLER.json").read_text())
ref = json.loads((B / "beklenen/OLCUMLER.json").read_text())
ANAHTAR = ["h1_bulgu_once", "h1_bulgu_sonra", "h1_katman_sayisi", "h1_nesne", "h2_masa", "h2_kisi", "h2_sandalye", "h2_toplam_tl",
           "h2_kisi_sandalye_uyumu", "h3_eklenen", "h3_silinen", "h3_koridor_gerekli_mm", "h3_koridor_rev1", "h3_koridor_rev2",
           "h4_pafta_sayisi", "h4_pdf_mm", "h4_olcek"]
hata = 0
for k in ANAHTAR:
    a, b = siz.get(k, "—yok—"), ref[k]
    ok = a == b; hata += not ok
    print(f"{'✓' if ok else '✗'} {k:24s} siz={a}  beklenen={b}")
print("SONUÇ:", "geçti" if hata == 0 else f"{hata} değer farklı")
