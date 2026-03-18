import fs from 'fs';
import path from 'path';

const veriYolu = './src/data/makine_verileri_temiz.json';
const resimKlasoru = './public/images';
const yeniVeriYolu = './src/data/makine_verileri_kusursuz.json';

console.log('Dayı, canavar eşleştirici motoru çalıştı...');

try {
    const mevcutResimler = fs.readdirSync(resimKlasoru);
    const makineler = JSON.parse(fs.readFileSync(veriYolu, 'utf-8'));

    const kusursuzMakineler = makineler.map(makine => {
        // Model ismini tamamen temizle (sadece harf ve rakam)
        const modelTemiz = makine.model.toLowerCase().replace(/[^a-z0-9]/g, '');
        
        // Klasördeki her bir resimle tek tek "Fuzzy" (esnek) karşılaştırma yap
        let enIyiEslesme = null;
        let enYuksekSkor = 0;

        mevcutResimler.forEach(dosya => {
            const dosyaTemiz = dosya.toLowerCase().replace(/[^a-z0-9]/g, '').replace('webp', '');
            
            // Eğer dosya ismi model ismini içeriyorsa veya tam tersi
            if (modelTemiz.includes(dosyaTemiz) || dosyaTemiz.includes(modelTemiz)) {
                // Skorlama yapıyoruz (ne kadar benzer o kadar iyi)
                const skor = dosyaTemiz.length > modelTemiz.length ? modelTemiz.length / dosyaTemiz.length : dosyaTemiz.length / modelTemiz.length;
                if (skor > enYuksekSkor) {
                    enYuksekSkor = skor;
                    enIyiEslesme = dosya;
                }
            }
        });

        return {
            ...makine,
            gercek_resim: enIyiEslesme ? `/images/${enIyiEslesme}` : 'https://via.placeholder.com/300x200?text=Resim+Bulunamadi'
        };
    });

    fs.writeFileSync(yeniVeriYolu, JSON.stringify(kusursuzMakineler, null, 2), 'utf-8');
    
    const bulunanlar = kusursuzMakineler.filter(m => !m.gercek_resim.includes('placeholder')).length;
    console.log(`Operasyon tamam dayı! ${bulunanlar} makineye resmi 'şak' diye oturttuk. ${makineler.length - bulunanlar} tane hala kayıp.`);

} catch (hata) {
    console.error('Dayı motor su kaynattı:', hata.message);
}