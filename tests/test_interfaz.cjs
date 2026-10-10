const {chromium}=require('playwright');
const fs=require('fs'),assert=require('assert/strict'),path=require('path');
const destino=path.resolve(__dirname,'../evidencias');
(async()=>{
 const browser=await chromium.launch({...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {}),headless:true});
 const context=await browser.newContext({viewport:{width:1600,height:1000}});
 const page=await context.newPage(),errores=[],comprobaciones=[];
 page.on('pageerror',e=>errores.push(e.message));
 const check=(nombre,valor)=>{assert.ok(valor,nombre);comprobaciones.push(nombre);};
 const foto=async nombre=>{await page.locator('#panel-desarrollo').evaluate(n=>n.scrollTop=0);await page.screenshot({path:path.join(destino,nombre+'.png')});};
 await page.goto(process.env.QA_BASE_URL || 'http://127.0.0.1:5010');await page.waitForFunction(()=>!document.querySelector('#ejecutar').disabled);
 check('Cinco opciones de navegación',await page.locator('[data-vista]').count()===5);
 check('Cuatro iconos del estilo original',await page.locator('.nav-icon').count()===4);
 check('Fondo de barra superior oscuro',await page.locator('.barra-superior').evaluate(n=>getComputedStyle(n).backgroundColor)==='rgb(51, 74, 120)');
 check('Cambios del usuario conservados',await page.locator('.sidebar-nota').count()===0 && await page.locator('#ayuda-mensaje').count()===0);
 async function operar(algoritmo,modo,mensaje,clave){
  await page.locator(`[data-vista="${algoritmo}"]`).click();await page.locator('#modo').selectOption(modo);await page.locator('#mensaje').fill(mensaje);
  if(modo!=='analizar'){if(algoritmo==='afin'){await page.locator('#clave-a').fill(String(clave.a));await page.locator('#clave-b').fill(String(clave.b));}else await page.locator('#clave').fill(clave);}
  await page.locator('#ejecutar').click();await page.waitForFunction(()=>!document.querySelector('#ejecutar').disabled);
 }
 await operar('cesar','cifrar','HOLA MUNDO','3');check('Caso 1 cifrado César',await page.locator('#resultado').innerText()==='KROD PXQGR');await foto('01_cesar_cifrado');
 await operar('cesar','descifrar','KROD PXQGR','3');check('Caso 1 descifrado César',await page.locator('#resultado').innerText()==='HOLA MUNDO');await foto('02_cesar_descifrado');
 check('Más reciente primero',await page.locator('#historial article').first().getAttribute('data-ejecucion')==='2');
 await operar('vigenere','cifrar','CRIPTOGRAFIA','SOL');check('Caso 2 cifrado Vigenère',await page.locator('#resultado').innerText()==='UFTHHZYFLXWL');await foto('03_vigenere_cifrado');
 check('Solo dos modos Vigenère',await page.locator('#modo option').count()===2);
 await operar('vigenere','descifrar','UFTHHZYFLXWL','SOL');check('Caso 2 descifrado Vigenère',await page.locator('#resultado').innerText()==='CRIPTOGRAFIA');await foto('04_vigenere_descifrado');
 await operar('sustitucion','cifrar','HOLA MUNDO','ZYXWVUTSRQPONMLKJIHGFEDCBA');check('Sustitución correcta',await page.locator('#resultado').innerText()==='SLOZ NFMWL');await foto('05_sustitucion');
 check('Solo dos modos Sustitución',await page.locator('#modo option').count()===2);
 await operar('sustitucion','descifrar','SLOZ NFMWL','ZYXWVUTSRQPONMLKJIHGFEDCBA');check('Mapa inverso',await page.locator('#resultado').innerText()==='HOLA MUNDO');
 for(const [alg,clave] of [['cesar','3'],['sustitucion','ZYXWVUTSRQPONMLKJIHGFEDCBA'],['vigenere','SOL'],['afin',{a:5,b:8}]]){
  await operar(alg,'cifrar','Hola, Mundo! 123 ¿Si?',clave);
  const r=await page.locator('#resultado').innerText();check(`Caso 3 conservación ${alg}`,r[4]===','&&r[5]===' '&&r.slice(-9)===' 123 ¿Dx?' ? alg==='cesar' : r[4]===','&&r[5]===' '&&r[11]==='!'&&r.includes('123 ¿')&&r.endsWith('?'));
 }
 await foto('06_caracteres_conservados');
 await operar('afin','cifrar','HOLA MUNDO',{a:5,b:8});check('Afín cifrado',await page.locator('#resultado').innerText()==='RALI QEVXA');await foto('07_afin_oscuro');
 await page.locator('[data-tema="claro"]').click();check('Tema claro',await page.locator('html').getAttribute('data-tema')==='claro');check('Barra clara',await page.locator('.barra-superior').evaluate(n=>getComputedStyle(n).backgroundColor)==='rgb(220, 231, 250)');await foto('08_afin_claro');
 await operar('afin','descifrar','RALI QEVXA',{a:5,b:8});check('Afín descifrado',await page.locator('#resultado').innerText()==='HOLA MUNDO');check('Euclides visible',(await page.locator('#historial article').first().innerText()).includes('Inverso modular: 21'));await foto('09_afin_descifrado');
 await operar('afin','analizar','RALI QEVXA');check('312 candidatos',await page.locator('#candidato option').count()===312);check('25 por página',await page.locator('#historial article').first().locator('.detalle-candidato').count()===25);
 await page.locator('#candidato').selectOption('a=5, b=8');check('Clave conocida encontrada',await page.locator('#resultado').innerText()==='HOLA MUNDO');check('Advertencia emergente',await page.locator('.notificacion.aviso').count()===1);await foto('10_afin_fuerza_bruta');
 await page.locator('.notificacion button').click();
 const tarjeta=page.locator('#historial article').first();await tarjeta.locator('button',{hasText:'Siguiente'}).click();check('Paginación',await tarjeta.locator('.paginacion').innerText().then(t=>t.includes('Página 2 de 13')));
 await tarjeta.locator('summary').first().click();await page.waitForFunction(()=>document.querySelector('#historial article .detalle-candidato[open] .paso-seccion'));check('Desarrollo bajo demanda',await tarjeta.locator('.detalle-candidato[open]').innerText().then(t=>t.includes('Inverso modular')));await foto('11_candidato_desarrollo');
 await operar('cesar','analizar','KROD PXQGR');check('25 candidatos César',await page.locator('#candidato option').count()===25);await page.locator('#candidato').selectOption('3');check('César candidato conocido',await page.locator('#resultado').innerText()==='HOLA MUNDO');await foto('12_cesar_fuerza_bruta');
 await operar('vigenere','cifrar','HOLA','');check('Caso 4 clave vacía',await page.locator('.notificacion[role="alert"]').innerText().then(t=>t.includes('vacía')));await foto('13_error_clave_vigenere');
 check('Error arriba a la derecha',await page.locator('#notificaciones').evaluate(n=>getComputedStyle(n).position==='fixed'&&n.getBoundingClientRect().right<=innerWidth));
 await operar('sustitucion','cifrar','HOLA','AAAAAAAAAAAAAAAAAAAAAAAAAA');check('Caso 5 clave repetida',await page.locator('.notificacion').innerText().then(t=>t.includes('duplicados')));await foto('14_error_sustitucion');
 await operar('afin','cifrar','HOLA',{a:2,b:8});check('Multiplicador inválido',await page.locator('.notificacion').innerText().then(t=>t.includes('coprimo')));await foto('15_error_afin');
 await operar('afin','cifrar','HOLA ñ',{a:5,b:8});check('Letra ajena rechazada',await page.locator('.notificacion').innerText().then(t=>t.includes('Símbolo no permitido')));await foto('16_error_caracter');
 await page.locator('.notificacion button').click();check('Cierre de alerta',await page.locator('.notificacion').count()===0);
 await page.locator('[data-vista="cesar"]').click();const nCesar=await page.locator('#historial article').count();check('Historial César independiente',nCesar===4);
 await page.locator('[data-vista="afin"]').click();await page.locator('#limpiar').click();check('Limpiar solo Afín',await page.locator('#historial article').count()===0);
 await page.locator('[data-vista="cesar"]').click();check('César conservado',await page.locator('#historial article').count()===nCesar);
 await page.locator('[data-vista="informacion"]').click();check('Cuatro pestañas teóricas',await page.locator('[data-tab]').count()===4);await page.locator('[data-tab="afin"]').click();check('Teoría Afín',await page.locator('#teoria-afin').isVisible());await foto('17_teoria');
 await page.setViewportSize({width:390,height:844});await page.locator('[data-vista="afin"]').click();check('Sin desbordamiento móvil',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await foto('18_movil');
 await page.reload();await page.waitForFunction(()=>!document.querySelector('#ejecutar').disabled);check('Tema conservado',await page.locator('html').getAttribute('data-tema')==='claro');check('Historial no persistente',await page.locator('#historial article').count()===0);
 check('Sin errores JavaScript',errores.length===0);
 fs.writeFileSync(path.join(destino,'interfaz.json'),JSON.stringify({comprobaciones,errores},null,2));console.log(`${comprobaciones.length} comprobaciones aprobadas`);await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
