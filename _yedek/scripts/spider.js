const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

const BASE_URL = 'https://www.yilmazmachine.com.tr';
const DOMAIN = 'yilmazmachine.com.tr';

let ziyaretEdilenler = new Set();
let kuyruk = [BASE_URL + '/tr/']; // TR ayağından başlıyoruz
let linkAgaci = [];

async function orumcekSal() {
    console.log("🕷️ Örümcek serbest bırakıldı, ağlar örülüyor dayı...");

    while (kuyruk.length > 0) {
        let suankiUrl = kuyruk.shift();

        if (ziyaretEdilenler.has(suankiUrl)) continue;
        ziyaretEdilenler.add(suankiUrl);

        try {
            console.log(`📡 taranıyor: ${suankiUrl} (Kalan: ${kuyruk.length})`);
            
            const response = await axios.get(suankiUrl, { 
                headers: { 'User-Agent': 'Mozilla/5.0' },
                timeout: 5000 
            });
            const $ = cheerio.load(response.data);

            $('a').each((i, el) => {
                let href = $(el).attr('href');
                if (!href) return;

                // Göreli linkleri tam URL'ye çevir (örn: /urunler/ -> https://.../urunler/)
                if (href.startsWith('/')) href = BASE_URL + href;

                // Sadece Yılmaz Machine'in iç linklerini ve henüz gitmediklerimizi al
                if (href.includes(DOMAIN) && !ziyaretEdilenler.has(href) && !kuyruk.includes(href)) {
                    // PDF, resim veya sosyal medya linklerini eleyelim (Veri tasarrufu!)
                    if (!href.match(/\.(pdf|jpg|jpeg|png|gif|zip|doc)$/i) && !href.includes('facebook') && !href.includes('linkedin')) {
                        kuyruk.push(href);
                        linkAgaci.push(href);
                    }
                }
            });

            // Her 10 sayfada bir dosyayı güncelle ki elektrik/internet giderse emekler zayi olmasın
            if (ziyaretEdilenler.size % 10 === 0) {
                fs.writeFileSync('./scripts/site_link_haritasi.json', JSON.stringify(Array.from(ziyaretEdilenler), null, 2));
            }

            // GÜVENLİK FRENİ: Mobil verin için şimdilik 200 sayfa sınırı koyalım mı?
            if (ziyaretEdilenler.size > 200) {
                console.log("🛑 Dayı 200 sayfa oldu, mobil verin yanmasın diye duruyorum!");
                break;
            }

        } catch (err) {
            console.log(`⚠️ ${suankiUrl} açılmadı, atladım.`);
        }
    }

    fs.writeFileSync('./scripts/site_link_haritasi.json', JSON.stringify(Array.from(ziyaretEdilenler), null, 2));
    console.log(`\n🏁 BİTTİ! Toplam ${ziyaretEdilenler.size} benzersiz link bulduk.`);
}

orumcekSal();