# AutoCAD Çizim Otomasyonu · öğrenci deposu

Forenly AI Academy kursu için çalışma deposu. Yürüyen örnek: bir kafede **insansı robotun (Unitree G1) çay servisi** yaptığı mekânın planı. Forenly AI'ın foi'si (Forenly Operational Intelligence) robotu böyle bir işletmenin içinde otonom çalıştırır. Bu yüzden çizim yalnız mimar için değil, robot için de doğru olmalı: robotun servis yolu açık kalmalı.

Önceki kursta (AutoCAD ile Tesis Yerleşim Planı) çizdiğiniz kafe planını bu kursta Python (ezdxf) ile **denetler, zenginleştirir ve paftaya dökersiniz**. Her sonucu AutoCAD'de açıp doğrularsınız.

| Hafta | Betik | Ne yapar | Ekibin ölçtüğü sonuç (11.10.2026) |
|---|---|---|---|
| 1 | `lab/h1_katman.py` | Dağınık çizimi katman standardına göre denetler (NCS/AIA adları ↔ ISO 13567), düzeltir, yeniden denetler | 9 bulgu → 0 |
| 2 | `lab/h2_oznitelik.py` | Öznitelikli masa bloğu (kod, kişi, malzeme, fiyat), robot istasyonu ve servis yolu; çizimden CSV + Excel metraj | 4 masa, 14 kişi, 14 sandalye, 55.400 TL (ÖRNEK) |
| 3 | `lab/h3_xref_fark.py` | Mimariyi dış referans (DWG) yapar, ikinci revizyonu üretir, farkı bulur ve işaretler, **robot koridorunu denetler** | 3 değişiklik; koridor rev1 850 mm ✓, rev2 0 mm ✗ (gereken 800 mm) |
| 4 | `lab/h4_pafta.py` | Pafta listesinden A3 yerleşimler, 1:50 görünüm penceresi, ISO 7200 antet, PDF seti | 3 sayfa × 420 × 297 mm, ölçek 1:50 |

## Kurulum

En kolayı GitHub Codespaces: **Code → Codespaces → Create**. Ortam kendiliğinden kurulur.
Kendi bilgisayarınızda: Python 3.10+ ve `pip install -r requirements.txt`.

## Koşum

```bash
cd lab
python h1_katman.py && python h2_oznitelik.py && python h3_xref_fark.py && python h4_pafta.py
cd .. && python kontrol.py
```

Çıktılar `lab/cikti/` (DXF, CSV, XLSX, PDF) ve `lab/ekran/` (PNG) altına yazılır. DXF'leri AutoCAD'de (AutoCAD Web dahil) açıp sonucu görün.
`h3` mimari planı dış referans olarak **DWG** bağlar (`kafe_mimari.dwg`, `beklenen/` içinde): AutoCAD DXF'i dış referans yapmaz, ezdxf de DWG yazamaz.

## Görevler

1. **Katman:** `h1_katman.py`'deki `ESLEM` tablosuna kendi çiziminizin katman adlarını ekleyin; denetim 0 bulguyla bitsin.
2. **Metraj:** `M-05` adında 6 kişilik yeni bir masa ekleyin. Kişi sayısı sandalye sayısıyla hâlâ tutuyor mu?
3. **Robot koridoru:** M-03 takımını kuzeye değil güneye 300 mm taşıyın. Koridor geçiyor mu? Robot genişliğini 500 mm yaparsanız ne olur?
4. **Claude Code katmanı:** Claude Code'a "A-104 adında, yalnız robot yolu ve istasyonu gösteren bir pafta ekle" deyin. Değişen satırları okuyun, PDF'i açın, `kontrol.py`'nin neden artık farklı dediğini açıklayın.

## Sınırlar

- Ölçüler, fiyatlar ve robot genişliği/payı **ÖRNEK**tir. Gerçek projede robot üreticisinin verisi ve iş güvenliği değerlendirmesi kullanılır.
- AutoCAD Web'de öznitelik tanımı (ATTDEF), yerleşim (LAYOUT), standart denetimi ve toplu çıktı komutları yok; bu işler burada Python ile yapılır, AutoCAD sonucu görmek ve ölçmek için kullanılır.
- AutoCAD Web'de View-only açılan DXF'te Türkçe harf (ş, ğ) bazen "?" çizilir; öznitelik değerleri bu yüzden ASCII seçildi. DWG olarak kaydedilen çizimde sorun yoktur.
