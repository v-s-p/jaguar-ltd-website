const fs = require('fs');
const https = require('https');
const http = require('http');
const path = require('path');
const sharp = require('sharp');

const xmlDosyasi = 'jaguar_data.xml';
const hedefKlasor = './resimler';

if (!fs.existsSync(hedefKlasor)) {
    fs.mkdirSync(hedefKlasor);
}

console.log('Dayı, filtreler takıldı, amortisörler devrede. İşlem başlıyor...');

try {
    const xmlIcerik = fs.readFileSync(xmlDosyasi, 'utf8');
    const urlRegex = /<wp:attachment_url>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?<\/wp:attachment_url>/g;
    let match;
    const urller = [];

    // Sadece gerçek resim formatlarını içeri alıyoruz (PDF vb. eleniyor)
    const gecerliUzantilar = /\.(jpg|jpeg|png|gif|webp)$/i;

    while ((match = urlRegex.exec(xmlIcerik)) !== null) {
        if (gecerliUzantilar.test(match[1])) {
            urller.push(match[1]);
        }
    }

    const benzersizUrller = [...new Set(urller)];
    
    if (benzersizUrller.length === 0) {
        console.log('Geçerli resim linki bulunamadı.');
    } else {
        console.log(`Filtreleme başarılı! Toplam ${benzersizUrller.length} GERÇEK resim preslenecek.`);

        benzersizUrller.forEach((url, index) => {
            const dosyaAdi = path.basename(url);
            const dosyaAdiWebp = dosyaAdi.replace(/\.[^/.]+$/, ".webp");
            const kayitYeri = path.join(hedefKlasor, dosyaAdiWebp);
            
            const protokol = url.startsWith('https') ? https : http;

            protokol.get(url, (cevap) => {
                if (cevap.statusCode === 200) {
                    const dosyaAkisi = fs.createWriteStream(kayitYeri);
                    const pres = sharp().webp({ quality: 80 });

                    // Amortisör: Sharp motoru hata verirse çökmek yerine atla
                    pres.on('error', (hata) => {
                        console.log(`[${index + 1}/${benzersizUrller.length}] ATLANDI (Bozuk/Geçersiz Dosya): ${dosyaAdi}`);
                        dosyaAkisi.close();
                    });

                    cevap.pipe(pres).pipe(dosyaAkisi);
                    
                    dosyaAkisi.on('finish', () => {
                        console.log(`[${index + 1}/${benzersizUrller.length}] Preslendi: ${dosyaAdiWebp}`);
                    });
                } else {
                    console.log(`[${index + 1}/${benzersizUrller.length}] Sunucu Yanıt Vermedi: ${dosyaAdi}`);
                }
            }).on('error', (hata) => {
                console.error(`Bağlantı koptu (${dosyaAdi}):`, hata.message);
            });
        });
    }
} catch (hata) {
    console.error('XML okunamadı:', hata.message);
}