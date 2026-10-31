import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {deliveryReply,replyLanguage} from './chat-replies.mjs';
for(const text of ['Kaç koli var?','kac koli var','URUN NEDIR','neden engellendi','Karar ne?','Selam'])assert.equal(replyLanguage(text),'tr',text);
for(const text of ['How many cartons are there?','What is the decision?','Show the product','hello'])assert.equal(replyLanguage(text,'tr'),'en',text);
assert.equal(replyLanguage('?', 'tr'),'tr');
for(const entry of JSON.parse(readFileSync(new URL('../data.json',import.meta.url))).cases){
 for(const [tr,en] of [['Kaç koli var?','How many cartons?'],['Ürün nedir?','What product?'],['Karar ne?','What is the decision?'],['Merhaba','Hello']]){
  const a=deliveryReply(tr,entry,'en'),b=deliveryReply(en,entry,'tr');
  assert.equal(a.language,'tr');assert.equal(b.language,'en');
  assert.ok(!a.text.includes('Recorded')&&!a.text.includes('Sunflower')&&!a.text.includes('Corn oil'));
  assert.ok(!b.text.includes('Ayçiçek')&&!b.text.includes('MISIR'));
  assert.ok(!a.text.includes('undefined')&&!b.text.includes('undefined'));
 }
 assert.ok(deliveryReply('kac koli var',entry).text.includes(String(entry.sam.sure)));
}
console.log('TR/EN replies, ASCII Turkish, language switching and six delivery records passed.');
