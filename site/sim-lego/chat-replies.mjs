import {english} from './replay.mjs?v=chat-3';
const normalize=text=>text.toLocaleLowerCase('tr-TR').replace(/ı/g,'i').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
export function replyLanguage(text,previous='en'){
 const words=normalize(text).match(/[a-z]+/g)||[];
 const tr=new Set('kac koli var mi nedir ne neden nasil sayim sayisi adet urun belge karar durum onay sonra merhaba selam lutfen tesekkur evet hayir tamam eksik hasarli yanlis geldi yapalim goster anlat bunu bu hangi gereken gerekiyor ver kabul iade sevkiyat'.split(' '));
 const en=new Set('how many cartons count quantity product document note decision status approve next hello hi please thanks yes no why what is are the this show explain damaged missing wrong delivery receipt'.split(' '));
 const t=words.filter(w=>tr.has(w)).length,e=words.filter(w=>en.has(w)).length;
 if(t!==e)return t>e?'tr':'en';
 return /[çğıöşüÇĞİÖŞÜ]/.test(text)?'tr':previous;
}
const reasonsTR={
 ok:'Ürün ve miktar eşleşiyor; kayıtlı mal kabul kontrolü onay verdi.',
 eksik:'İrsaliyede 12 koli var, ancak 11 koli geldi. Eksik miktar nedeniyle stok kaydı engellendi.',
 wrong:'Yanlış ürün: irsaliyede ayçiçek yağı, palet etiketlerinde mısır yağı yazıyor. Stok kaydı engellendi.',
 hasarli:'Bir koli hasarlı. Sağlam 11 kolinin kabulü ve hasarlı kolinin karantinaya ayrılması için şef değerlendirmesi gerekiyor.',
 talimat:'Belgede sayımı atlamaya yönelik gömülü talimat bulundu. Talimat uygulanmadı; bağımsız doğrulanmış temiz belge gerekiyor.',
 belirsiz:'Koliler istifli veya gizli; kamera görüntüsünden kesin sayım yapılamıyor. İstif açılarak yeniden sayım gerekiyor.'
};
const productTR=text=>String(text).replace(/Sunflower oil/gi,'Ayçiçek yağı').replace(/Corn oil/gi,'Mısır yağı');
export function deliveryReply(text,entry,previous='en'){
 const language=replyLanguage(text,previous),tr=language==='tr',prompt=normalize(text),note=entry.note.items[0];
 const reason=tr?(reasonsTR[entry.id]||'Bu teslimatın kayıtlı kararını kanıtlar bölümünde inceleyebilirsin.'):english(entry.gate.reason);
 let answer;
 if(/\b(count|cartons|quantity|many|koli|sayim|sayisi|adet|kac)\b/.test(prompt))answer=tr
  ?`Kayıtlı sayım: ${entry.sam.sure} kesin, ${entry.sam.doubtful} şüpheli koli. İrsaliyedeki miktar: ${note.quantity} koli. ${reason}`
  :`Recorded count: ${entry.sam.sure} sure, ${entry.sam.doubtful} doubtful. Delivery note: ${note.quantity} cartons. ${reason}`;
 else if(/\b(product|urun|note|belge|document|irsaliye)\b/.test(prompt))answer=tr
  ?`İrsaliye: ${productTR(note.description)}, ${note.quantity} koli. Palet etiketleri: ${productTR(entry.spark.product_on_labels)}. ${reason}`
  :`Delivery note: ${english(note.description)}, ${note.quantity} cartons. Pallet labels: ${english(entry.spark.product_on_labels)}. ${reason}`;
 else if(/\b(decision|karar|next|sonra|approve|onay|durum|status|kabul|iade)\b/.test(prompt))answer=tr
  ?`Kayıtlı karar: ${{post:'ONAY',block:'ENGELLENDİ',human:'ŞEF DEĞERLENDİRMESİ'}[entry.gate.action]||'İNCELEME'}. ${reason} Ayrı simülasyon kararını mal kabul iş akışından verebilirsin; sohbet teslimatı onaylamaz veya değiştirmez.`
  :`Recorded decision: ${entry.gate.action.toUpperCase()}. ${reason} Use the receiving workflow for the separate simulated handling decision; this chat does not approve or change a delivery.`;
 else answer=tr
  ?`Teslimat kaydına göre: ${reason} Sayım, ürün veya karar hakkında soru sorabilirsin. Bu sohbet teslimatı onaylamaz veya değiştirmez.`
  :`From the delivery record: ${reason} You can ask about the count, product or decision. This chat does not approve or change a delivery.`;
 return {text:answer,language};
}
