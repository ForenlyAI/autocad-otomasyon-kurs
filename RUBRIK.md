# Bitirme işi ve ölçüt çizelgesi

**Bitirme işi:** kendi seçtiğiniz bir mekânın kat planı DXF'ini katman standardına uydurun, öznitelikli bloklarla metrajını çıkarın ve en az iki A3 paftayı (1:50) tek komutla bir PDF setine dökün. Sonuçları AutoCAD'de (AutoCAD Web yeterli) açıp doğrulayın.

Teslim: PDF seti · son DXF (ya da DWG) · metraj (CSV ya da XLSX) · denetim çıktısı · kısa not (hangi adımı Claude Code'a yaptırdınız, nasıl doğruladınız).

Her ölçütü kendiniz denetleyebilirsiniz; "nasıl denetlenir" sütunu yapılacak işi söyler.

| Ölçüt | Yeterli | Eksik | Nasıl denetlenir |
|---|---|---|---|
| Katman standardı | Denetim betiği 0 bulgu veriyor; adlar tek bir standarda (NCS ya da ISO 13567) uyuyor | Bulgu kalmış ya da adlar karışık | `h1_katman.py`'deki denetimi kendi dosyanızda koşun · AutoCAD'de katman paleti |
| Öznitelik ve metraj | Tekrarlanan eşya öznitelikli blok; metraj çizimden üretilmiş ve toplam doğru | Metraj elle yazılmış ya da çizimle tutmuyor | Metrajı yeniden üretin, toplamı AutoCAD'de bir bloğa tıklayıp özellikler paneliyle karşılaştırın |
| Tutarlılık denetimi | Bilgi ile geometri arasında en az bir denetim var ve bilerek bozulmuş bir kopyada hatayı yakalıyor | Denetim yok ya da hiç sınanmamış | Bir kopyada bir nesneyi silip denetimin kaldığını gösterin |
| Ölçek | Her paftada görünüm penceresi 1:50 (ya da beyan ettiğiniz ölçek); oran betikle okunmuş | Ölçek gözle ayarlanmış, oran okunmamış | `view_height / height` oranı (Ders 4.2) |
| Pafta ve antet | A3 yatay, çerçeve (sol 20 mm, öteki 10 mm), antetin 6 alanı veriden dolu | Antet elle yazılmış ya da boş alan var | PDF'i açıp antete bakın; pafta numaraları sıralı |
| PDF seti | En az 2 sayfa, her sayfa 420 × 297 mm | Sayfa boyutu farklı ya da paftalar ayrı dosyalarda | `pypdf` ile sayfa sayısı ve boyutu (Ders 4.4) |
| Claude Code ile doğrulama | Claude Code'a yaptırılan her değişiklikten sonra kontrol ya da AutoCAD ile doğrulama yapılmış ve notta yazılı | Değişiklik okunmadan kabul edilmiş | Notunuzdaki komut ve doğrulama çıktısı |

**Geçme koşulu:** yedi ölçütün en az beşi "yeterli", ilk ikisi zorunlu. Ölçüleri ve fiyatları siz seçtiyseniz teslimde ÖRNEK diye yazın.

İsteğe bağlı (artı puan): planınızda bir robot ya da araç yolu varsa Ders 3.4'teki koridor denetimini iki revizyonda koşun.

Not: bu kurs AutoCAD Web'de hazırlandı. AutoCAD Web'de olmayan komutlar (ATTDEF, LAYOUT, PUBLISH, AutoLISP) bitirme işinde istenmez; bu işler Python ile yapılır.
