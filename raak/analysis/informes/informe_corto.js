// [raak local] Informe corto para el profesor (05-10): art (AF2) frente a RAA k=0..3, nodos y CPU por instancia.
// Lee resumen.json, la tabla CSV y las figuras de results/09-informes (los genera analysis/art_vs_raa.py) y escribe ahi el .docx.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  AlignmentType, ImageRun, LevelFormat, BorderStyle, ShadingType, Footer, PageNumber, LineRuleType,
} = require("docx");

const DIR = path.resolve(__dirname, "..", "..", "results", "09-informes");
const OUT = path.join(DIR, "Informe_art_vs_RAA_nodos_y_cpu_2026-10-05.docx");
const resumen = JSON.parse(fs.readFileSync(path.join(DIR, "resumen.json"), "utf8"));
const csv = fs.readFileSync(path.join(DIR, "tabla_por_instancia_art_vs_raa.csv"), "utf8").trim().split(/\r?\n/);
const head = csv[0].split(",");
const tabla = csv.slice(1).map(l => Object.fromEntries(l.split(",").map((v, i) => [head[i], v])));

const FONT = "Calibri";
const INK = "0B0B0B", INK2 = "52514E", RULE = "D9D7D1", HEAD_BG = "EEF3FA", SET_BG = "F4F3EF";
const PAGE_W = 12240, MARGIN = 1000, CONTENT_W = PAGE_W - 2 * MARGIN;

function run(text, o = {}) {
  return new TextRun({ text, font: o.code ? "Consolas" : FONT, size: o.size || 21, bold: o.bold, italics: o.italics, color: o.color || INK });
}
function rich(text, base = {}) {
  const parts = []; const re = /(`[^`]+`|\*\*[^*]+\*\*)/g; let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(run(text.slice(last, m.index), base));
    const t = m[0];
    parts.push(t.startsWith("`") ? run(t.slice(1, -1), { ...base, code: true, size: (base.size || 21) - 2 }) : run(t.slice(2, -2), { ...base, bold: true }));
    last = m.index + t.length;
  }
  if (last < text.length) parts.push(run(text.slice(last), base));
  return parts;
}
const p = (text, o = {}) => new Paragraph({ children: rich(text, o), spacing: { after: o.after ?? 100, line: 264, lineRule: LineRuleType.AUTO }, keepNext: o.keepNext });
const h1 = (t, o = {}) => new Paragraph({ text: t, heading: HeadingLevel.HEADING_1, spacing: { before: 280, after: 100 }, keepNext: true, pageBreakBefore: !!o.newPage });
const h2 = (t) => new Paragraph({ text: t, heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 80 }, keepNext: true });
const bullets = (items) => items.map(t => new Paragraph({ children: rich(t), numbering: { reference: "bul", level: 0 }, spacing: { after: 60, line: 264 } }));
const spacer = (after = 100) => new Paragraph({ spacing: { after }, children: [] });

function table(header, rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cols = widths.map(w => Math.round(CONTENT_W * w / total));
  const b = { style: BorderStyle.SINGLE, size: 4, color: RULE };
  const borders = { top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b };
  const mk = (cells, kind) => new TableRow({
    tableHeader: kind === "head", cantSplit: true,
    children: cells.map((c, i) => new TableCell({
      width: { size: cols[i], type: WidthType.DXA },
      columnSpan: (kind === "group" && i === 0) ? cells.length : undefined,
      shading: kind === "head" ? { fill: HEAD_BG, type: ShadingType.CLEAR, color: "auto" } : kind === "group" ? { fill: SET_BG, type: ShadingType.CLEAR, color: "auto" } : undefined,
      margins: { top: 35, bottom: 35, left: 70, right: 70 },
      children: [new Paragraph({ children: rich(String(c), { bold: kind !== "body", size: o.size || 19 }), spacing: { after: 0, line: 230 },
        alignment: (o.right && o.right.includes(i) && kind === "body") ? AlignmentType.RIGHT : undefined })],
    })).filter((_, i) => !(kind === "group" && i > 0)),
  });
  const body = rows.map(r => Array.isArray(r) ? mk(r, "body") : mk([r.group], "group"));
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: cols, borders, rows: header ? [mk(header, "head"), ...body] : body });
}
function pngSize(buf) { return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) }; }
function figure(file, caption, widthIn = 6.4) {
  const buf = fs.readFileSync(path.join(DIR, file)); const { w, h } = pngSize(buf);
  const W = Math.round(widthIn * 96), H = Math.round(W * h / w);
  return [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 40 }, keepNext: true, children: [new ImageRun({ type: "png", data: buf, transformation: { width: W, height: H } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: rich(caption, { color: INK2, size: 18, italics: true }) })];
}
const f3 = x => x.toFixed(3);
const fcells = v => v === "" ? "—" : Number(v).toLocaleString("es-CL").replace(/\./g, " ");
const fcpu = v => { if (v === "") return "—"; const x = Number(v); return x < 0.1 ? x.toFixed(3) : x < 10 ? x.toFixed(2) : x < 1000 ? x.toFixed(1) : Math.round(x).toString(); };
const ESTADO = { TIME_OUT: "límite 1800 s", UNBOUNDED_OBJ: "no acotada", INFEASIBLE: "infactible", NO_FEASIBLE_FOUND: "sin punto factible", SIN_DATO: "sin dato" };

// ---------------------------------------------------------------- contenido
const ch = [];
ch.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [run("art frente a RAA (k = 0, 1, 2, 3): nodos y CPU por instancia", { size: 34, bold: true })] }));
ch.push(new Paragraph({ spacing: { after: 40 }, children: [run("Eva Ponce Fernández · Juan Carlos Geraldo — guía: Dr. Ignacio Araya (PUCV) — 5 de octubre de 2026", { size: 20, color: INK2 })] }));
ch.push(new Paragraph({ spacing: { after: 200 }, children: [run("Versión reducida del informe del 30 de septiembre, con solo la comparación pedida. Datos: etapas B y D de la Fase 3 (relajación art, límite 1800 s de CPU por corrida) más la corrida de k=2 del 5 de octubre con la misma configuración. Todo lo demás sigue en el informe completo y en raak/ del repo.", { size: 20, color: INK2 })] }));

ch.push(h1("1. Qué se compara"));
ch.push(p("Las cuatro configuraciones corren el mismo `ibexopt-raak` con la relajación afín sola (`--lr=art`), mismos parámetros del B&B (filtrado `acidhc4`, bisección `lsmearmg`, semilla 42) y límite de 1800 s de CPU. Solo cambia la aritmética afín con la que se construye la relajación:", { keepNext: true }));
ch.push(table(["columna", "qué es", "flags", "estado"], [
  ["art (AF2)", "La aritmética del plugin tal cual (fAF2). Es la base.", "`--arith=af2 --knomial_k=0`", "corrida"],
  ["RAA k=0", "AF2 + parte cuadrática de la RAA: forma simétrica, cuadrados de Chebyshev, corner test. Sin bloques k-nomiales.", "`--arith=raa --knomial_k=0`", "corrida"],
  ["RAA k=1", "Idéntica a k=0: la reescritura k-nomial necesita cliques de al menos 2 variables, así que con k=1 no extrae nada y el código sigue exactamente el camino de k=0. Equivale al antiguo `raak_k=1` del prototipo.", "`--knomial_k=1`", "= k=0, no se repite"],
  ["RAA k=2", "RAA + bloques de hasta 2 variables (binomios).", "`--arith=raa --knomial_k=2`", "corrida (5 de octubre, ver §6)"],
  ["RAA k=3", "RAA + bloques de hasta 3 variables.", "`--arith=raa --knomial_k=3`", "corrida"],
], [13, 50, 22, 15], { size: 18 }));
ch.push(spacer());
ch.push(p("**Instancias:** las 147 de `benchs/optim` en `easy` (101), `medium` (31), `hard` (7) y `others` (8). **Métricas:** celdas = nodos procesados por el B&B; CPU = tiempo medido por el optimizador; en todas las instancias resueltas las cuatro configuraciones dan el mismo intervalo de óptimo. 11 instancias no se resuelven con ninguna (2 agotan el tiempo, 6 no acotadas, 1 infactible, 2 sin punto factible): van en la tabla con su estado."));

ch.push(h1("2. Resumen"));
const R = resumen;
function filaRes(g, v, lab) {
  const f = R[g][v];
  return [lab, `${f.resueltas} / ${f.n}`, f3(f.gm_celdas), `${f.celdas_gana} / ${f.celdas_empata} / ${f.celdas_pierde}`, f3(f.gm_cpu), `${f.cpu_gana} / ${f.cpu_empata} / ${f.cpu_pierde}`, fcpu(f.cpu_total_h * 3600)];
}
const resRows = [];
for (const [g, lab] of [["easy+medium", "easy + medium (132 instancias)"], ["hard+others", "hard + others (15 instancias)"], ["todas", "todas (147 instancias)"]]) {
  resRows.push({ group: lab });
  resRows.push(filaRes(g, "art_af2_k0", "art (AF2), base"));
  resRows.push(filaRes(g, "art_raa_k0", "RAA k=0 (= k=1)"));
  resRows.push(filaRes(g, "art_raa_k2", "RAA k=2"));
  resRows.push(filaRes(g, "art_raa_k3", "RAA k=3"));
}
ch.push(table(["configuración", "resueltas", "celdas: media geom. vs art", "celdas: gana / empata / pierde", "CPU: media geom. vs art", "CPU: gana / empata / pierde", "CPU total (s)"], resRows, [20, 11, 14, 16, 13, 16, 10], { size: 18, right: [1, 2, 3, 4, 5, 6] }));
ch.push(p("Media geométrica del cociente configuración / art sobre las instancias resueltas por ambas (1 = igual; menor es mejor). Gana = cociente < 0.95, pierde = > 1.05. CPU total = suma sobre las instancias resueltas.", { color: INK2, size: 18 }));
const k2 = R["todas"]["k2_vs_k0"], k3 = R["todas"]["k3_vs_k0"], k32 = R["todas"]["k3_vs_k2"];
ch.push(p(`**Efecto de k dentro de RAA (${k3.comparables} instancias resueltas):** frente a k=0, k=2 da media geométrica de celdas ${f3(k2.gm_celdas)} y de CPU ${f3(k2.gm_cpu)} (${k2.celdas_gana} instancias mejoran más de 5 %, ${k2.celdas_pierde} empeoran, ${k2.identicas} con exactamente las mismas celdas); k=3 da ${f3(k3.gm_celdas)} y ${f3(k3.gm_cpu)} (${k3.celdas_gana} mejoran, ${k3.celdas_pierde} empeoran, ${k3.identicas} idénticas). Entre k=2 y k=3: ${k32.identicas} de ${k32.comparables} idénticas. Los bloques k-nomiales solo llegan a extraerse en la familia \`ex14_2_*\`; en el resto de las instancias ningún producto tiene dos factores que compartan símbolos, así que k no cambia nada.`));

ch.push(h2("Instancias donde RAA cambia más (RAA k=0 frente a art)"));
ch.push(table(["instancia", "art: celdas", "art: CPU (s)", "RAA k=0: celdas", "RAA k=0: CPU (s)", "celdas RAA / art"],
  R.top_raa.map(t => [t.instancia, fcells(t.art), fcpu(t.art_cpu), fcells(t.raa), fcpu(t.raa_cpu), f3(t.ratio)]), [26, 15, 14, 16, 15, 14], { size: 18, right: [1, 2, 3, 4, 5] }));
ch.push(p("Las tres primeras vienen del cuadrado de Chebyshev de la RAA (acota `sqr` de una forma compuesta por su rango exacto); las demás son diferencias pequeñas. Las 4 a 5 instancias donde RAA pierde más de 5 % son todas de pocas celdas (entre 14 y 400) y la diferencia es de un puñado de nodos.", { color: INK2, size: 18 }));

ch.push(h1("3. Gráficos"));
ch.push(...figure("dispersion_art_vs_raa.png", "Figura 1. Cada punto es una instancia: en x lo que necesitó art, en y lo que necesitó RAA (k=0 círculos, k=2 signos más, k=3 cruces). Sobre la diagonal, iguales; debajo, RAA mejor. Escala log en ambos ejes."));
ch.push(p("Casi todos los puntos están sobre la diagonal: en la gran mayoría de las instancias las cuatro configuraciones recorren exactamente los mismos nodos. Los dos puntos muy por debajo son `ex8_4_4bis` y `ex8_4_5bis` (celdas ÷ 11, CPU ÷ 9), y el tercero `bearing` (celdas × 0.64). Círculos, signos más y cruces coinciden: ni k=2 ni k=3 se separan de k=0."));
ch.push(...figure("perfiles_art_vs_raa.png", "Figura 2. Perfiles de desempeño. Para cada instancia, celdas (o CPU) divididas por las de la mejor configuración; la curva dice qué fracción de instancias queda dentro de un factor X de la mejor. Más arriba, mejor."));
ch.push(p("Las cuatro curvas van superpuestas: en celdas, art parte del 88 % y las RAA del 90 % en x = 1, y la diferencia visible es la cola de art hacia la derecha (las tres instancias de arriba). En CPU, RAA k=0 va ligeramente por encima en todo el rango (media geométrica 0.959)."));

ch.push(h1("4. Tabla completa por instancia", { newPage: true }));
ch.push(p("Celdas = nodos del B&B; CPU en segundos. Donde la instancia no se resuelve, la última columna dice por qué (es el mismo estado en las cuatro configuraciones) y las celdas y la CPU son las alcanzadas hasta ese momento.", { color: INK2, size: 18 }));
const rows = [];
let setActual = null;
const SETLAB = { easy: "easy", medium: "medium", hard: "hard", others: "others" };
for (const r of tabla) {
  if (r.set !== setActual) { setActual = r.set; rows.push({ group: SETLAB[r.set] }); }
  const est = r.art_af2_k0_estado;
  const nota = est === "SUCCESS" ? "" : (ESTADO[est] || est);
  rows.push([r.instancia, fcells(r.art_af2_k0_celdas), fcpu(r.art_af2_k0_cpu), fcells(r.art_raa_k0_celdas), fcpu(r.art_raa_k0_cpu), fcells(r.art_raa_k2_celdas), fcpu(r.art_raa_k2_cpu), fcells(r.art_raa_k3_celdas), fcpu(r.art_raa_k3_cpu), nota]);
}
ch.push(table(["instancia", "art: celdas", "art: CPU", "RAA k=0 (=k=1): celdas", "RAA k=0: CPU", "RAA k=2: celdas", "RAA k=2: CPU", "RAA k=3: celdas", "RAA k=3: CPU", "estado"], rows, [17, 10, 9, 11, 9, 10, 9, 10, 9, 12], { size: 15, right: [1, 2, 3, 4, 5, 6, 7, 8] }));
ch.push(spacer());

ch.push(h1("5. Conclusiones", { newPage: true }));
ch.push(...bullets([
  `**RAA frente a art.** RAA nunca resuelve menos: 136 de 147 en ambas. En celdas es igual o mejor en todo salvo ruido (${R.todas.art_raa_k0.celdas_gana} gana / ${R.todas.art_raa_k0.celdas_pierde} pierde más de 5 %; media 0.963), y en CPU baja un 4 % en promedio (${R.todas.art_raa_k0.cpu_gana} gana / ${R.todas.art_raa_k0.cpu_pierde} pierde). Su costo por evaluación es nulo en la práctica. La ganancia se concentra en instancias con cuadrados de expresiones compuestas: ahí divide los nodos por 11.`,
  `**k = 0, 1, 2, 3.** k=1 es k=0 por construcción. k=2 y k=3 frente a k=0 son neutros: ${k2.identicas} y ${k3.identicas} de ${k3.comparables} instancias con exactamente las mismas celdas, medias ${f3(k2.gm_celdas)} y ${f3(k3.gm_celdas)}. La reescritura k-nomial solo encuentra material en \`ex14_2_*\`, porque en el producto de dos formas afines la matriz es de rango 2 y casi nunca hay dos símbolos compartidos; donde actúa, el efecto en celdas va en los dos sentidos y es del tamaño del ruido del B&B.`,
  "**Qué usar hoy con `art`.** RAA k=0. Lo que la RAA aporta al solver en estas instancias es su parte cuadrática (cuadrados de Chebyshev), no los bloques k-nomiales.",
]));

ch.push(h1("6. Nota sobre la corrida de k = 2"));
ch.push(p("Las etapas B y D de septiembre solo tenían k=0 y k=3. La columna k=2 se corrió el 5 de octubre con el mismo binario, parches, parámetros y límite (`scripts/wsl_fase3_k2_launch.sh` reutiliza `wsl_fase3_sweep.sh` con la variante `--lr=art --arith=raa --knomial_k=2`), sobre las mismas 147 instancias, 12 procesos en paralelo. Las filas están en `results/07-fase3-nivel2-solver/fase3-k2-20261005/art_raa_k2/runs.csv` y en WSL en `~/ibex-local/results/fase3-k2-20261005/`. La tabla por instancia y este documento se generan con `art_vs_raa.py` e `informe_corto.js`, también en la carpeta."));

ch.push(h1("Dónde está todo"));
ch.push(table(["qué", "ruta"], [
  ["Datos de este documento", "`raak/results/07-fase3-nivel2-solver/fase3-20260921/B_easy_medium_art/runs.csv` y `D_hard_others_art/runs.csv`; k=2: `raak/results/07-fase3-nivel2-solver/fase3-k2-20261005/art_raa_k2/runs.csv`"],
  ["Tabla por instancia en CSV, figuras y resumen", "`raak/results/09-informes/`"],
  ["Informe completo del 30 de septiembre", "`raak/results/09-informes/Informe_RAAK_comparacion_aritmeticas_2026-09-30.pdf`"],
  ["Resultados con `compo` y con la AA tradicional", "`raak/results/07-fase3-nivel2-solver/fase3-20260921/RESUMEN.md`"],
], [30, 70], { size: 18 }));

const doc = new Document({
  creator: "Eva Ponce Fernández", title: "art frente a RAA (k = 0, 1, 2, 3): nodos y CPU por instancia",
  styles: {
    default: { document: { run: { font: FONT, size: 21, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 28, bold: true, color: "1F3A5F" }, paragraph: { spacing: { before: 280, after: 100 }, outlineLevel: 0 } },
      { id: "Heading2", name: "heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 23, bold: true, color: "1F3A5F" }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 250 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 15840 }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ font: FONT, size: 16, color: INK2, children: ["art frente a RAA · página ", PageNumber.CURRENT] })] })] }) },
    children: ch,
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log("escrito:", OUT, Math.round(buf.length / 1024), "KB"); });
