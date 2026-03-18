const fs = require('fs');

const dosyaYolu = 'makine_verileri.json';
const yeniDosyaYolu = 'makine_verileri_temiz.json';

console.log('Dayı, shortcode çorbası süzülüyor, makine etleri ayıklanıyor...');

const veriler = JSON.parse(fs.readFileSync(dosyaYolu, 'utf-8'));

const temizVeriler = veriler.map(makine => {
    const icerik = makine.tam_icerik;

    // 1. YouTube Linkini Ayıkla
    const videoMatch = icerik.match(/vc_video link="(.*?)"/);
    const videoLink = videoMatch ? videoMatch[1] : null;

    // 2. Başlıkları Bul (ld_fancy_heading içindekiler)
    const basliklar = icerik.match(/\[ld_fancy_heading.*?\](.*?)\[\/ld_fancy_heading\]/g) || [];
    const temizBasliklar = basliklar.map(b => b.replace(/\[.*?\]/g, ''));

    // 3. Listeleri Ayıkla (Standart ve Opsiyonel Aksesuarlar)
    const listeler = icerik.match(/\[ld_list.*?\](.*?)\[\/ld_list\]/g) || [];
    const temizListeler = listeler.map(l => {
        return l.replace(/\[.*?\]/g, '').split(',').map(item => item.trim());
    });

    // 4. Ana Tanıtım Metnini Bul
    const tanitimMatch = icerik.match(/vc_custom_heading text="(.*?)"/);
    const tanitim = tanitimMatch ? tanitimMatch[1] : '';

    return {
        model: makine.baslik,
        dil: makine.dil,
        tanitim: tanitim,
        ozellikler: temizListeler[2] || [], // Genelde 3. liste teknik özelliklerdir
        standart_aksesuarlar: temizListeler[0] || [],
        opsiyonel_aksesuarlar: temizListeler[1] || [],
        video: videoLink,
        eski_link: makine.eski_link
    };
});

fs.writeFileSync(yeniDosyaYolu, JSON.stringify(temizVeriler, null, 2), 'utf-8');
console.log(`Dayı işlem tamam! ${temizVeriler.length} makine jilet gibi temizlendi.`);