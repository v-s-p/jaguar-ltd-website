const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

const TEST_URL = 'https://www.yilmazmachine.com.tr/urunler/kd-402-s/';

async function teshisEt() {
    console.log("🕵️ Sayfa yapısı inceleniyor dayı... Büyüteç elimde.");

    try {
        const res = await axios.get(TEST_URL, { headers: { 'User-Agent': 'Mozilla/5.0' } });
        const $ = cheerio.load(res.data);

        // 1. Gerçek makine adını bulalım (Genelde .product_title veya h2 içindedir)
        let makineAdi = $('.product_title').text().trim() || $('.title').text().trim() || $('h2').first().text().trim();
        console.log(`📌 Bulunan Makine Adı: ${makineAdi}`);

        // 2. Teknik tabloyu arayalım
        let tabloVerisi = [];
        
        // Eğer klasik tablo varsa
        $('table tr').each((i, el) => {
            const tdler = $(el).find('td');
            if (tdler.length >= 2) {
                tabloVerisi.push({
                    ozellik: $(tdler[0]).text().trim(),
                    deger: $(tdler[1]).text().trim()
                });
            }
        });

        // Eğer tablo yoksa, liste yapısını (.technical-specs vb.) kontrol et
        if (tabloVerisi.length === 0) {
            console.log("🤔 Klasik tablo yok, liste yapısına bakıyorum...");
            $('.technical-specs li, .spec-item').each((i, el) => {
                tabloVerisi.push($(el).text().trim());
            });
        }

        const sonuc = {
            url: TEST_URL,
            isim: makineAdi,
            veriler: tabloVerisi
        };

        fs.writeFileSync('./scripts/teshis_sonuc.json', JSON.stringify(sonuc, null, 2));
        console.log("🏁 Teşhis bitti. 'scripts/teshis_sonuc.json' dosyasını bir aç bakalım, bu sefer bir şeyler var mı?");

    } catch (err) {
        console.error("❌ Sayfaya ulaşılamadı: ", err.message);
    }
}

teshisEt();