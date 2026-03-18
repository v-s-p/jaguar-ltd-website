const fs = require('fs');
const xml2js = require('xml2js');

const xmlDosyasi = 'jaguar_data.xml';
const ciktiDosyasi = 'makine_verileri.json';

console.log('Dayı, XML süzgeci çalıştırılıyor. Veriler ayıklanıyor...');

const parser = new xml2js.Parser();

fs.readFile(xmlDosyasi, (err, data) => {
    if (err) {
        console.error('Dosya okuma hatası:', err);
        return;
    }

    parser.parseString(data, (err, result) => {
        if (err) {
            console.error('XML ayrıştırma hatası:', err);
            return;
        }

        // WordPress'in karmaşık yapısına dalıyoruz
        const items = result.rss.channel[0].item;
        const makineler = [];

        items.forEach(item => {
            // Sadece makine sayfalarını (portfolio) ve yayınlanmış olanları alalım
            // Not: Sitenizdeki post_type "portfolio" veya "post" olabilir, kontrol ediyoruz
            const postType = item['wp:post_type'][0];
            const status = item['wp:status'][0];

            if ((postType === 'portfolio' || postType === 'post') && status === 'publish') {
                const baslik = item.title[0];
                const icerik = item['content:encoded'][0];
                const link = item.link[0];
                
                // WPML dil bilgisini çekmeye çalışalım (varsa)
                let dil = 'bg'; // Varsayılan Bulgarca
                if (link.includes('/en/')) {
                    dil = 'en';
                }

                makineler.push({
                    baslik: baslik,
                    dil: dil,
                    aciklama: icerik ? icerik.replace(/<[^>]*>?/gm, '').trim().substring(0, 200) + '...' : '', // Temiz metin özeti
                    tam_icerik: icerik,
                    eski_link: link
                });
            }
        });

        // Veriyi JSON olarak kaydet
        fs.writeFileSync(ciktiDosyasi, JSON.stringify(makineler, null, 2), 'utf-8');
        console.log(`İşlem tamam! ${makineler.length} adet makine verisi süzüldü ve ${ciktiDosyasi} dosyasına kaydedildi.`);
    });
});