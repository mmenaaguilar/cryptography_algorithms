/* Datos del servidor se insertan como texto, nunca como HTML. */
"use strict";
const $ = id => document.getElementById(id);
const nombres = {cesar: "César", sustitucion: "Sustitución Simple", vigenere: "Vigenère", afin: "Afín"};
const titulos = {cesar: "Cifrado César", sustitucion: "Sustitución Simple", vigenere: "Cifrado Vigenère", afin: "Cifrado Afín"};
const etiquetas = {cifrar: "Cifrar", descifrar: "Descifrar", analizar: "Fuerza bruta"};
const clavesPorAlgoritmo = {cesar: "3", sustitucion: "QWERTYUIOPASDFGHJKLZXCVBNM", vigenere: "SOL", afin: ""};
let algoritmo = "cesar", configuracion, ocupado = false, salidaCopiable = null;

const estados = Object.fromEntries(Object.keys(nombres).map(nombre => [nombre, {
  mensaje: "HOLA MUNDO", modo: "cifrar", clave: clavesPorAlgoritmo[nombre],
  a: "5", b: "8", tarjetas: [], secuencia: 0, resumen: null, candidato: null, error: null, scroll: 0
}]));
function aplicarTema(tema) {
  if (!["oscuro", "claro"].includes(tema)) tema = "oscuro";
  document.documentElement.dataset.tema = tema;
  document.querySelectorAll("button[data-tema]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.tema === tema)));
  try { localStorage.setItem("criptografia-tema", tema); } catch {}
}
let temaInicial = "oscuro";
try { temaInicial = localStorage.getItem("criptografia-tema") || temaInicial; } catch {}
aplicarTema(temaInicial);
document.querySelectorAll("button[data-tema]").forEach(b => b.addEventListener("click", () => aplicarTema(b.dataset.tema)));
const elemento = (tag, clase = "", texto = undefined) => {
  const nodo = document.createElement(tag);
  if (clase) nodo.className = clase;
  if (texto !== undefined) nodo.textContent = String(texto);
  return nodo;
};
const siguienteFrame = () => new Promise(resolve => requestAnimationFrame(resolve));
const visible = c => ({" ": "espacio", "\t": "tabulación", "\n": "salto de línea", "\r": "retorno"}[c] || c);

function limpiarErrores() {
  ["mensaje", "clave", "clave-a", "clave-b"].forEach(campo => {
    $(campo).removeAttribute("aria-invalid");
    if ($("error-" + campo)) { $("error-" + campo).hidden = true; $("error-" + campo).textContent = ""; }
  });
  $("feedback").textContent = "";
  $("notificaciones").replaceChildren();
}
function notificar(tipo, titulo, mensaje) {
  const contenedor = $("notificaciones");
  if ([...contenedor.children].some(n => n.dataset.mensaje === mensaje)) return;
  while (contenedor.children.length >= 3) contenedor.firstElementChild.remove();
  const nodo = elemento("div", "notificacion" + (tipo === "aviso" ? " aviso" : ""));
  nodo.dataset.mensaje = mensaje; nodo.setAttribute("role", tipo === "error" ? "alert" : "status");
  const texto = elemento("div"); texto.append(elemento("strong", "", titulo), elemento("p", "", mensaje));
  const cerrar = elemento("button", "", "×"); cerrar.type = "button"; cerrar.setAttribute("aria-label", "Cerrar notificación");
  cerrar.onclick = () => nodo.remove();
  nodo.append(elemento("span", "notificacion-icono", tipo === "error" ? "!" : "⚠"), texto, cerrar); contenedor.append(nodo);
  if (tipo === "aviso") {
    let timer; const iniciar = () => { clearTimeout(timer); timer = setTimeout(() => nodo.remove(), 8000); };
    const pausar = () => clearTimeout(timer);
    nodo.addEventListener("mouseenter", pausar); nodo.addEventListener("mouseleave", iniciar);
    nodo.addEventListener("focusin", pausar); nodo.addEventListener("focusout", iniciar); iniciar();
  }
}
function mostrarError(error, enfocar = true) {
  estados[algoritmo].error = error;
  const campo = ["mensaje", "clave", "clave-a", "clave-b"].includes(error.campo) ? error.campo : "mensaje";
  $(campo).setAttribute("aria-invalid", "true");
  if (enfocar) notificar("error", "No se pudo ejecutar", error.error || "Revisa los datos.");
  $("estado").textContent = "Revisa la entrada";
  $("estado").className = "estado error";
  $("resultado").className = "resultado error";
  $("resultado").textContent = "Corrige el campo indicado y vuelve a ejecutar.";
  $("metadato").textContent = "La operación se ha bloqueado antes de calcular.";
  $("selector-candidato").hidden = true;
  $("original-resumen").hidden = true;
  habilitarSalida(null);
  if (enfocar) $(campo).focus();
}
function habilitarSalida(salida) {
  salidaCopiable = salida;
  $("copiar").disabled = salida === null;
  $("reutilizar").disabled = salida === null;
}
function actualizarFormulario() {
  const modo = $("modo").value;
  $("titulo-algoritmo").textContent = titulos[algoritmo];
  $("ejecutar").textContent = ocupado ? "Procesando…" : etiquetas[modo];
  $("grupo-clave").hidden = modo === "analizar" || algoritmo === "afin";
  $("grupo-afin").hidden = modo === "analizar" || algoritmo !== "afin";
  $("ayuda-modo").hidden = modo !== "analizar";
  $("ayuda-modo").textContent = {cesar: "Se probarán los 25 desplazamientos no triviales.", afin: "Se probarán las 312 claves válidas. Los resultados son candidatos."}[algoritmo];
  const ayudas = {
    cesar: ["Desplazamiento", "Entero positivo, negativo o cero. Se aplica módulo 26.", "numeric"],
    sustitucion: ["Alfabeto sustituto", "Las 26 letras A–Z, sin repeticiones. La primera sustituye a A.", "text"],
    afin: ["Clave Afín", "Dos enteros a y b.", "numeric"],
    vigenere: ["Clave", "Solo letras inglesas A–Z. Los signos del mensaje no consumen clave.", "text"]
  };
  const [label, ayuda, inputmode] = ayudas[algoritmo];
  $("label-clave").textContent = label;
  $("ayuda-clave").textContent = ayuda;
  $("clave").inputMode = inputmode;
  $("clave").value = clavesPorAlgoritmo[algoritmo];
}
function guardarFormulario() {
  const estado = estados[algoritmo];
  estado.mensaje = $("mensaje").value; estado.modo = $("modo").value;
  estado.a = $("clave-a").value; estado.b = $("clave-b").value;
  estado.clave = $("clave").value; clavesPorAlgoritmo[algoritmo] = estado.clave;
  estado.candidato = $("candidato").value; estado.scroll = $("panel-desarrollo").scrollTop;
}
function contarHistorial() {
  const total = estados[algoritmo].tarjetas.length;
  $("cuenta-historial").textContent = `${nombres[algoritmo]} · ${total} ${total === 1 ? "ejecución" : "ejecuciones"} · Más reciente primero · Temporal`;
  $("historial").setAttribute("aria-label", `Historial de ${nombres[algoritmo]}`);
}
function mostrarHistorial() {
  const tarjetas = estados[algoritmo].tarjetas;
  $("historial").replaceChildren(...tarjetas);
  if (!tarjetas.length) {
    const vacio = elemento("div", "vacio"); vacio.id = "vacio";
    vacio.append(elemento("span", "vacio-numero", "01"), elemento("h3", "", "Tu procedimiento aparecerá aquí"), elemento("p", "", "Cada algoritmo tiene su propio historial. La nueva ejecución aparecerá primero; puedes revisar todos sus cálculos."), elemento("div", "mini-alfabeto", "A=0   B=1   …   Z=25"));
    $("historial").append(vacio);
  }
  contarHistorial();
}
function restaurarAlgoritmo() {
  const estado = estados[algoritmo];
  $("modo").replaceChildren(...["cifrar", "descifrar", ...(["cesar", "afin"].includes(algoritmo) ? ["analizar"] : [])].map(m => {
    const opcion = elemento("option", "", etiquetas[m]); opcion.value = m; return opcion;
  }));
  $("clave-a").value = estado.a; $("clave-b").value = estado.b;
  $("mensaje").value = estado.mensaje; $("modo").value = estado.modo;
  clavesPorAlgoritmo[algoritmo] = estado.clave;
  limpiarErrores(); actualizarFormulario(); $("mensaje").dispatchEvent(new Event("input"));
  if (estado.resumen) {
    actualizarResumen(estado.resumen);
    if (estado.candidato && estado.resumen.tipo === "fuerza_bruta") {
      $("candidato").value = estado.candidato; $("candidato").dispatchEvent(new Event("change"));
    }
  } else {
    $("estado").textContent = "Listo"; $("estado").className = "estado";
    $("metadato").textContent = "La salida aparecerá después de ejecutar.";
    $("resultado").className = "resultado placeholder"; $("resultado").textContent = "Esperando una operación.";
    $("selector-candidato").hidden = true; $("original-resumen").hidden = true; habilitarSalida(null);
  }
  if (estado.error) mostrarError(estado.error, false);
  mostrarHistorial(); $("panel-desarrollo").scrollTop = estado.scroll;
}
document.querySelectorAll("[data-vista]").forEach(boton => boton.addEventListener("click", () => {
  if (ocupado) return;
  guardarFormulario();
  const vista = boton.dataset.vista;
  document.querySelectorAll("[data-vista]").forEach(item => {
    const activo = item === boton; item.classList.toggle("active", activo);
    if (activo) item.setAttribute("aria-current", "page"); else item.removeAttribute("aria-current");
  });
  const teoria = vista === "informacion";
  $("panel-operacion").hidden = teoria; $("panel-desarrollo").hidden = teoria; $("panel-informacion").hidden = !teoria;
  if (!teoria) { algoritmo = vista; restaurarAlgoritmo(); }
}));
$("modo").addEventListener("change", () => { clavesPorAlgoritmo[algoritmo] = $("clave").value; limpiarErrores(); actualizarFormulario(); });
$("mensaje").addEventListener("input", () => { $("contador").textContent = `${Array.from($("mensaje").value).length} caracteres`; });
$("clave").addEventListener("input", () => { clavesPorAlgoritmo[algoritmo] = $("clave").value; });

function seleccionarTab(nombre) {
  document.querySelectorAll("[data-tab]").forEach(tab => {
    const activo = tab.dataset.tab === nombre;
    tab.setAttribute("aria-selected", String(activo)); tab.tabIndex = activo ? 0 : -1;
    $("teoria-" + tab.dataset.tab).hidden = !activo;
  });
}
const tabs = [...document.querySelectorAll("[data-tab]")];
tabs.forEach((tab, indice) => {
  tab.addEventListener("click", () => seleccionarTab(tab.dataset.tab));
  tab.addEventListener("keydown", event => {
    let siguiente;
    if (event.key === "ArrowRight") siguiente = (indice + 1) % tabs.length;
    if (event.key === "ArrowLeft") siguiente = (indice + tabs.length - 1) % tabs.length;
    if (event.key === "Home") siguiente = 0;
    if (event.key === "End") siguiente = tabs.length - 1;
    if (siguiente !== undefined) { event.preventDefault(); seleccionarTab(tabs[siguiente].dataset.tab); tabs[siguiente].focus(); }
  });
});

function validarCliente() {
  const mensaje = $("mensaje").value;
  if (!mensaje) return {error: "Ingresa un mensaje para continuar.", campo: "mensaje"};
  const maximo = $("modo").value === "analizar" ? configuracion.maximo_analisis : configuracion.maximo_mensaje;
  if (Array.from(mensaje).length > maximo) return {error: `El máximo para esta operación es ${maximo} caracteres. El texto no se ha recortado.`, campo: "mensaje"};
  const permitidos = new Set(configuracion.permitidos);
  let linea = 1, columna = 1, anterior = "";
  for (const caracter of mensaje) {
    if (!permitidos.has(caracter)) return {error: `Símbolo no permitido: ${JSON.stringify(caracter)} (línea ${linea}, columna ${columna}). Corrige el mensaje para continuar.`, campo: "mensaje"};
    if (caracter === "\r") { linea++; columna = 1; }
    else if (caracter === "\n") { if (anterior !== "\r") linea++; columna = 1; }
    else columna++;
    anterior = caracter;
  }
  return null;
}
function seccion(contenedor, numero, titulo) {
  const bloque = elemento("section", "paso-seccion");
  const h = elemento("h3", "paso-titulo");
  h.append(elemento("span", "paso-numero", String(numero).padStart(2, "0")), elemento("span", "", titulo));
  const contenido = elemento("div", "contenido-paso"); bloque.append(h, contenido); contenedor.append(bloque);
  return contenido;
}
function linea(contenedor, etiqueta, valor, clase = "") {
  const p = elemento("p", "datos-linea"); p.append(document.createTextNode(etiqueta + ": "), elemento("span", clase, valor)); contenedor.append(p);
}
function tabla(contenedor, cabeceras) {
  const scroll = elemento("div", "table-scroll"), t = elemento("table"), head = elemento("thead"), tr = elemento("tr"), body = elemento("tbody");
  cabeceras.forEach(titulo => { const th = elemento("th", "", titulo); th.scope = "col"; tr.append(th); });
  head.append(tr); t.append(head, body); scroll.append(t); contenedor.append(scroll); return body;
}
function celda(texto, clase = "") { return elemento("td", clase, texto); }
function formula(contenedor, registro) {
  const nodo = elemento("div", "formula");
  if (registro.algoritmo === "sustitucion") nodo.textContent = registro.formula;
  else registro.formula.split(/([PCKk](?:ᵢ)?|\d+)/g).forEach(token => {
    let clase = "";
    if (/^\d+$/.test(token)) clase = "valor";
    if (/^[Kk]/.test(token)) clase = "clave";
    if (/^[PC]/.test(token)) {
      const entrada = registro.modo === "cifrar" ? "P" : "C";
      clase = token.startsWith(entrada) ? "entrada" : "salida";
    }
    nodo.append(elemento("span", clase, token));
  });
  contenedor.append(nodo);
}
async function tablaPasos(contenedor, registro) {
  const vigenere = registro.algoritmo === "vigenere";
  const cabeceras = vigenere ? ["Paso", "Entrada", "Valor", "Clave · índice", "Valor clave", "Cálculo", "Salida"] : ["Paso", "Entrada", "Valor", "Cálculo", "Salida"];
  const body = tabla(contenedor, cabeceras);
  for (let inicio = 0; inicio < registro.pasos.length; inicio += 120) {
    const fragmento = document.createDocumentFragment();
    registro.pasos.slice(inicio, inicio + 120).forEach(paso => {
      const fila = elemento("tr");
      fila.append(celda(paso.posicion), celda(visible(paso.entrada), paso.letra ? "entrada" : "token-preservado"), celda(paso.valor_entrada ?? "—", "valor"));
      if (vigenere) fila.append(celda(paso.clave_letra ? `${paso.clave_letra} · ${paso.indice_clave}` : "—", "clave"), celda(paso.valor_clave ?? "—", "valor"));
      const calculo = celda("", "calculo");
      if (paso.letra && registro.algoritmo !== "sustitucion" && registro.algoritmo !== "afin") {
        const operador = registro.modo === "cifrar" ? "+" : "−";
        const desarrollo = `(${paso.valor_entrada} ${operador} ${paso.valor_clave}) = ${paso.antes_modulo}; ${paso.antes_modulo} mod 26 = ${paso.valor_salida}`;
        desarrollo.split(/(-?\d+)/g).forEach(token => calculo.append(elemento("span", /^-?\d+$/.test(token) ? "valor" : "", token)));
      } else if (paso.letra && registro.algoritmo === "afin") paso.calculo.split(/(-?\d+)/g).forEach(token => calculo.append(elemento("span", /^-?\d+$/.test(token) ? "valor" : "", token)));
      else calculo.textContent = paso.calculo;
      fila.append(calculo, celda(visible(paso.salida), paso.letra ? "salida" : "token-preservado")); fragmento.append(fila);
    });
    body.append(fragmento);
    if (registro.pasos.length > 120) await siguienteFrame();
  }
}
function reconstruccion(contenedor, registro) {
  contenedor.append(elemento("div", "reconstruccion", registro.pasos.map(p => p.letra ? p.salida : `[${visible(p.salida)}]`).join(" + ")));
  contenedor.append(elemento("p", "nota", "Resultado final"), elemento("pre", "final-traza salida", registro.resultado));
  const progresivo = elemento("div", "progreso");
  const label = elemento("label", "", "Construcción progresiva"), rango = elemento("input");
  rango.type = "range"; rango.min = "1"; rango.max = String(registro.pasos.length); rango.value = rango.max;
  rango.setAttribute("aria-label", "Paso de la construcción progresiva");
  const estado = elemento("span", "nota"), prefijo = elemento("pre", "salida");
  const actualizar = () => {
    const posicion = Number(rango.value); estado.textContent = `Paso ${posicion} de ${registro.pasos.length}`;
    prefijo.textContent = registro.resultado.slice(0, posicion);
  };
  rango.addEventListener("input", actualizar); actualizar();
  progresivo.append(label, rango, estado, prefijo); contenedor.append(progresivo);
}
async function renderTransformacion(contenedor, registro, incluirDatos = true) {
  if (incluirDatos) {
    const datos = seccion(contenedor, 1, "Datos iniciales");
    datos.append(elemento("pre", "mensaje-traza entrada", registro.mensaje));
    linea(datos, "Clave", registro.clave, "clave"); datos.append(elemento("span", "datos-linea correcto", "Entrada válida"));
    const preparacion = seccion(contenedor, 2, "Preparación");
    linea(preparacion, "Alfabeto", registro.alfabeto);
    const equivalencias = elemento("p", "datos-linea");
    registro.alfabeto.split("").forEach((letra, i) => { equivalencias.append(document.createTextNode(`${letra}=`), elemento("span", "valor", i), document.createTextNode(i === 25 ? "" : "  ")); });
    preparacion.append(equivalencias);
    if (registro.algoritmo === "cesar") linea(preparacion, "Desplazamiento efectivo", registro.clave_efectiva, "clave");
    if (registro.algoritmo === "afin") {
      linea(preparacion, "Clave efectiva", registro.clave, "clave");
      linea(preparacion, "Coprimalidad", `mcd(${registro.clave_efectiva.a},26) = 1`, "valor");
      if (registro.modo === "descifrar") {
        linea(preparacion, "Inverso modular", registro.inverso, "valor");
        const euclides = tabla(preparacion, ["División", "Actualización del coeficiente"]);
        registro.euclides.forEach(e => { const fila = elemento("tr"); fila.append(celda(`${e.dividendo} = ${e.cociente} × ${e.divisor} + ${e.resto}`, "valor"), celda(`${e.t_anterior} − ${e.cociente} × (${e.t_actual}) = ${e.t_nuevo}`, "valor")); euclides.append(fila); });
        linea(preparacion, "Verificación", `(${registro.clave_efectiva.a} × ${registro.inverso}) mod 26 = 1`, "valor");
      }
    }
    if (registro.algoritmo === "sustitucion") {
      linea(preparacion, "Alfabeto sustituto", registro.clave, "clave");
      preparacion.append(elemento("p", "nota", "Permutación validada: 26 letras sin duplicados. Se utiliza el mapa " + (registro.modo === "cifrar" ? "directo." : "inverso.")));
      const mapa = tabla(preparacion, ["Entrada", "Salida"]);
      for (let i = 0; i < 26; i++) { const tr = elemento("tr"); tr.append(celda(registro.modo === "cifrar" ? registro.alfabeto[i] : registro.clave[i], "entrada"), celda(registro.modo === "cifrar" ? registro.clave[i] : registro.alfabeto[i], "salida")); mapa.append(tr); }
    }
    if (registro.algoritmo === "vigenere") {
      linea(preparacion, "Clave repetida", registro.clave, "clave");
      const alineacion = tabla(preparacion, ["Posición", "Carácter", "Letra procesada", "Clave"]);
      registro.pasos.forEach(p => { const tr = elemento("tr"); tr.append(celda(p.posicion), celda(visible(p.entrada), p.letra ? "entrada" : "token-preservado"), celda(p.numero_letra ?? "—", "valor"), celda(p.clave_letra ?? "No consume", p.letra ? "clave" : "token-preservado")); alineacion.append(tr); });
    }
    formula(seccion(contenedor, 3, "Fórmula"), registro);
  }
  await tablaPasos(seccion(contenedor, 4, "Cálculo por carácter"), registro);
  reconstruccion(seccion(contenedor, 5, "Construcción del resultado"), registro);
}
async function renderAnalisis(contenedor, registro) {
  const datos = seccion(contenedor, 1, "Datos y alcance");
  datos.append(elemento("pre", "mensaje-traza entrada", registro.mensaje), elemento("p", "nota", registro.explicacion));
  linea(datos, "Letras procesadas", registro.total_letras, "valor");
  const candidatos = seccion(contenedor, 2, `${registro.candidatos.length} claves candidatas`);
  const pagina = elemento("div"); const navegacion = elemento("div", "paginacion");
  const anterior = elemento("button", "", "Anterior"), siguiente = elemento("button", "", "Siguiente"), contador = elemento("span", "nota");
  anterior.type = siguiente.type = "button"; navegacion.append(anterior, contador, siguiente); candidatos.append(navegacion, pagina);
  let indice = 0; const tamano = 25, total = Math.ceil(registro.candidatos.length / tamano);
  function dibujar() {
    pagina.replaceChildren(); contador.textContent = `Página ${indice + 1} de ${total}`;
    anterior.disabled = indice === 0; siguiente.disabled = indice === total - 1;
    registro.candidatos.slice(indice * tamano, (indice + 1) * tamano).forEach((c, offset) => {
      const detalle = elemento("details", "detalle-candidato");
      const summary = elemento("summary", "", `Intento ${indice * tamano + offset + 1} · ${c.clave}${c.identidad ? " · Sin transformación" : ""}`);
      detalle.append(summary, elemento("pre", "mensaje-traza salida", c.resultado));
      const pasos = elemento("div"); detalle.append(pasos); pagina.append(detalle);
      let cargando = false, cargado = false;
      detalle.addEventListener("toggle", async () => {
        if (!detalle.open || cargado || cargando) return;
        cargando = true;
        try {
          let completo = c;
          if (!c.pasos) {
            const respuesta = await fetch("/api/operar", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({algoritmo: registro.algoritmo, modo: "descifrar", mensaje: registro.mensaje, clave: c.clave_efectiva})});
            completo = await respuesta.json(); if (!respuesta.ok) throw new Error(completo.error);
          }
          await renderTransformacion(pasos, completo); cargado = true;
        } catch { pasos.replaceChildren(); notificar("error", "No se pudo cargar el desarrollo", "Comprueba el servidor y vuelve a abrir el candidato."); }
        finally { cargando = false; }
      });
    });
  }
  anterior.onclick = () => { indice--; dibujar(); }; siguiente.onclick = () => { indice++; dibujar(); }; dibujar();
}
function actualizarResumen(registro) {
  $("estado").textContent = "Completado"; $("estado").className = "estado ok";
  $("metadato").textContent = `${nombres[registro.algoritmo]} · ${etiquetas[registro.modo]}` + (registro.clave !== undefined ? ` · Clave ${registro.clave}` : "");
  $("texto-original").textContent = registro.mensaje; $("original-resumen").hidden = false;
  $("selector-candidato").hidden = true; $("resultado").className = "resultado";
  if (registro.tipo === "transformacion") { $("resultado").textContent = registro.resultado; habilitarSalida(registro.resultado); }
  else if (registro.tipo === "fuerza_bruta") {
    $("selector-candidato").hidden = false; $("candidato").replaceChildren();
    registro.candidatos.forEach(c => { const op = elemento("option", "", `Clave ${c.clave}`); op.value = c.clave; $("candidato").append(op); });
    const elegir = () => { const c = registro.candidatos.find(item => item.clave === $("candidato").value); $("resultado").textContent = c.resultado; habilitarSalida(c.resultado); $("metadato").textContent = `${nombres[registro.algoritmo]} · Candidato seleccionado · ${c.clave} · Sin confirmación`; };
    $("candidato").onchange = elegir; elegir();
  } else {
    $("resultado").className = "resultado placeholder";
    $("resultado").textContent = registro.tipo === "frecuencias" ? `${registro.total_letras} letras analizadas. Consulta los conteos y porcentajes en el procedimiento.` : `${registro.repeticiones.length} fragmentos repetidos. ${registro.candidatos.length} longitudes candidatas. Consulta el desarrollo; ninguna clave está confirmada.`;
    habilitarSalida(null);
  }
}
$("formulario").addEventListener("submit", async event => {
  event.preventDefault(); if (ocupado || !configuracion) return;
  limpiarErrores(); const error = validarCliente(); if (error) { mostrarError(error); return; }
  ocupado = true; $("ejecutar").disabled = true; $("limpiar").disabled = true;
  $("ejecutar").textContent = "Procesando…";
  try {
    const respuesta = await fetch("/api/operar", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({algoritmo, modo: $("modo").value, mensaje: $("mensaje").value, clave: algoritmo === "afin" ? {a: $("clave-a").value, b: $("clave-b").value} : $("clave").value})});
    const registro = await respuesta.json();
    if (!respuesta.ok) { mostrarError(registro); return; }
    const estado = estados[algoritmo];
    estado.resumen = registro; estado.error = null; estado.candidato = null;
    actualizarResumen(registro);
    if (registro.tipo === "fuerza_bruta") notificar("aviso", "Candidatos sin confirmar", "La búsqueda terminó. Ningún resultado se confirma automáticamente como mensaje original.");
    $("vacio")?.remove(); estado.secuencia++;
    const tarjeta = elemento("article", "registro"); tarjeta.dataset.ejecucion = estado.secuencia;
    tarjeta.append(elemento("p", "registro-meta", `Ejecución ${String(estado.secuencia).padStart(2, "0")} · ${nombres[registro.algoritmo]} · ${etiquetas[registro.modo]}`));
    estado.tarjetas.unshift(tarjeta); $("historial").prepend(tarjeta); contarHistorial();
    if (registro.tipo === "transformacion") await renderTransformacion(tarjeta, registro); else await renderAnalisis(tarjeta, registro);
    $("panel-desarrollo").scrollTop = 0; guardarFormulario();
  } catch (error) { mostrarError({error: "No se pudo completar la operación. Comprueba que el servidor local sigue abierto y vuelve a intentarlo.", campo: "mensaje"}); }
  finally { ocupado = false; $("ejecutar").disabled = false; $("limpiar").disabled = false; actualizarFormulario(); }
});
$("copiar").addEventListener("click", async () => {
  if (salidaCopiable === null) return;
  try { await navigator.clipboard.writeText(salidaCopiable); $("feedback").textContent = "Resultado copiado."; }
  catch { notificar("aviso", "Portapapeles no disponible", "Selecciona el resultado y cópialo manualmente."); }
});
$("reutilizar").addEventListener("click", () => {
  if (salidaCopiable === null || ocupado) return;
  $("mensaje").value = salidaCopiable; $("mensaje").dispatchEvent(new Event("input")); limpiarErrores(); $("mensaje").focus();
  $("feedback").textContent = "Resultado cargado como entrada. Elige la siguiente operación.";
});
$("limpiar").addEventListener("click", () => {
  if (ocupado) return;
  estados[algoritmo].tarjetas = []; estados[algoritmo].scroll = 0; mostrarHistorial();
  $("panel-desarrollo").scrollTop = 0;
});
mostrarHistorial();
fetch("/api/config").then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(datos => { configuracion = datos; $("ejecutar").disabled = false; }).catch(() => mostrarError({error: "No se pudo cargar la configuración. Recarga la página con el servidor abierto.", campo: "mensaje"}));
