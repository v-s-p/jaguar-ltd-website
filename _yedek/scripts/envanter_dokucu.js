const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

// Örümceğin getirdiği haritayı yüklüyoruz
const linkHaritasi = JSON.parse(fs.readFileSync('./scripts/site_link_haritasi.json', 'utf8'));

const BASE_URL = 'https://www.yilmazmachine.com.tr';

async function envanterDök() {
    console.log("📋 Envanter dökümü başlıyor dayı... Çekmeceleri hazırladım.");
    
    // Sadece kategori linklerini ayıkla
    const kategoriLinkleri = linkHaritasi.filter(link => link.includes('/urun_kategori/'));
    let masterEnvanter = {};

    for (let katUrl of kategoriLinkleri) {
        try {
            // Kategori adını URL'den çek (Örn: 'isleme-merkezleri')
            const katSlug = katUrl.split('/').filter(Boolean).pop();
            console.log(`📂 Kategori taranıyor: ${katSlug}`);
            
            const res = await axios.get(katUrl, { headers: { 'User-Agent': 'Mozilla/5.0' } });
            const $ = cheerio.load(res.data);
            
            masterEnvanter[katSlug] = {
                url: katUrl,
                makineler: []
            };

            // Sayfadaki ürün linklerini bul
            $('a').each((i, el) => {
                const href = $(el).attr('href');
                const isim = $(el).text().trim();

                // Sizin keşfettiğiniz '/urunler/' yapısına odaklanıyoruz
                if (href && href.includes('/urunler/') && isim.length > 2) {
                    const fullUrl = href.startsWith('http') ? href : BASE_URL + href;
                    
                    // Tekrarı önle
                    if (!masterEnvanter[katSlug].makineler.find(m => m.url === fullUrl)) {
                        masterEnvanter[katSlug].makineler.push({
                            isim: isim,
                            url: fullUrl,
                            slug: fullUrl.split('/').filter(Boolean).pop()
                        });
                    }
                }
            });
            console.log(`   ✅ ${masterEnvanter[katSlug].makineler.length} makine bulundu.`);

        } catch (err) {
            console.log(`⚠️ ${katUrl} okunurken bir kablo koptu, atlıyorum.`);
        }
    }

    // Sonucu tertemiz bir dosya olarak yaz
    fs.writeFileSync('./scripts/makine_envanteri_master.json', JSON.stringify(masterEnvanter, null, 2));
    console.log("\n🏁 BİTTİ DAYI! 'scripts/makine_envanteri_master.json' hazır.");
}

envanterDök();