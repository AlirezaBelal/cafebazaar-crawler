import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {test} from 'node:test';
const html=await readFile(new URL('../site/index.html',import.meta.url),'utf8');
test('publication is static and explains the real collection boundary',()=>{
  assert(html.includes("script-src 'none'"));assert(html.includes("connect-src 'none'"));
  assert(!/<script|<iframe|<form|src="https:/i.test(html));
  assert(html.includes('https://alirezabelal.github.io/cafebazaar-crawler/'));
  assert(html.includes('static product guide'));assert(html.includes('not global request limits'));
});
test('documented commands use supported flags and local assets exist',async()=>{
  const cli=await readFile(new URL('../src/main.py',import.meta.url),'utf8');
  for(const flag of ['--category-limit','--subcategory-limit','--max-apps','--max-list-pages','--max-subcategory-pages','--demo','--report','--export-csv']){assert(html.includes(flag));assert(cli.includes(flag));}
  for(const asset of ['styles.css','assets/mark.svg','assets/collection-flow.svg'])assert((await readFile(new URL('../site/'+asset,import.meta.url))).length>0);
});
