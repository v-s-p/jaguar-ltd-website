const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');

const BASE_URL = 'https://www.yilmazmachine.com.tr';
const ANA_KATEGORILER = [
    { ad: 'Alüminyum', url: '/urun_kategori/aluminyum/' },
    { ad: 'PVC', url: '/urun_kategori/pvc/' }
];

async function zırhlıOperasyon() {
    console.log("🚀 Motorlar yeniden kükrüyor dayı... Bu sefer beton dolacak!");
    let veritabani = { "Alüminyum": {}, "PVC": {} };

    try {
        for (let ana of ANA_KATEGORILER) {
            console.log(`\n📂 ${ana.ad} sayfası taranıyor: ${BASE_URL}${ana.url}`);
            const response = await axios.get(`${BASE_URL}${ana.url}`, { 
                headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' } 
            });
            const $ = cheerio.load(response.data);

            // STRATEJİ: Sayfadaki TÜM linkleri tara, içinde 'urun_kategori' geçenleri al ama ana kategoriyi ele.
            $('a').each((i, el) => {
                const link = $(el).attr('href');
                const isim = $(el).text().trim();

                if (link && link.includes('/urun_kategori/') && !link.endsWith('/aluminyum/') && !link.endsWith('/pvc/')) {
                    const fullUrl = link.startsWith('http') ? link : `${BASE_URL}${link}`;
                    
                    // İsim 3 karakterden büyükse ve daha önce eklenmediyse gerçek bir alt kategoridir
                    if (isim.length > 3 && !veritabani[ana.ad][isim]) {
                        veritabani[ana.ad][isim] = { url: fullUrl, urunler: [] };
                    }
                }
            });

            const bulunanGrupSayisi = Object.keys(veritabani[ana.ad]).length;
            console.log(`✅ ${ana.ad} için ${bulunanGrupSayisi} gerçek alt grup tespit edildi.`);

            // Her alt grubun içine sızıp makineleri toplayalım
            for (let grupAd in veritabani[ana.ad]) {
                const grup = veritabani[ana.ad][grupAd];
                try {
                    const res = await axios.get(grup.url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
                    const $grup = cheerio.load(res.data);

                    $grup('a').each((j, urunEl) => {
                        const uLink = $grup(urunEl).attr('href');
                        const uIsim = $grup(urunEl).text().trim();

                        // Eğer link /urun/ içeriyor ve bir ismi varsa bu bir makinedir
                        if (uLink && uLink.includes('/urun/') && uIsim.length > 2) {
                            const fullULink = uLink.startsWith('http') ? uLink : `${BASE_URL}${uLink}`;
                            
                            // Tekrarı önle
                            if (!grup.urunler.find(u => u.url === fullULink)) {
                                grup.urunler.push({ ad: uIsim, url: fullULink });
                            }
                        }
                    });
                    if (grup.urunler.length > 0) {
                        console.log(`   📦 ${grupAd}: ${grup.urunler.length} makine yakalandı.`);
                    }
                } catch (e) {
                    console.log(`   ⚠️ ${grupAd} taranırken küçük bir taş çarptı (Atlanıyor).`);
                }
            }
        }

        // Dolu dosyayı yazalım
        fs.writeFileSync('./scripts/makine_listesi_tam_Dolu.json', JSON.stringify(veritabani, null, 2));
        console.log("\n🏁 İŞLEM TAMAM DAYI! 'scripts/makine_listesi_tam_Dolu.json' artık boş değil.");

    } catch (err) {
        console.error("❌ Kritik hata: ", err.message);
    }
}

zırhlıOperasyon();