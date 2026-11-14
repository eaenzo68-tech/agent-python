// Coloration syntaxique minimale pour Python (aucune bibliothèque externe).
// Renvoie du HTML où chaque morceau de code est échappé puis entouré d'un <span>.

const MOTS_CLES = new Set([
  "False", "None", "True", "and", "as", "assert", "async", "await", "break", "class",
  "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global",
  "if", "import", "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
  "return", "try", "while", "with", "yield",
]);

const INTEGRES = new Set([
  "print", "input", "len", "range", "int", "float", "str", "bool", "list", "dict", "tuple",
  "set", "sum", "min", "max", "abs", "round", "sorted", "reversed", "enumerate", "zip",
  "type", "isinstance", "open", "map", "filter", "any", "all", "self", "super",
  "ValueError", "TypeError", "KeyError", "IndexError", "ZeroDivisionError", "Exception",
]);

// Un seul motif qui reconnaît, dans l'ordre : commentaire, chaîne, nombre, nom, espaces, symbole.
const MOTIF = new RegExp([
  "(#[^\\n]*)",
  "((?:[rRbBfFuU]{1,2})?(?:\"\"\"[\\s\\S]*?(?:\"\"\"|$)|'''[\\s\\S]*?(?:'''|$)|\"(?:\\\\.|[^\"\\\\\\n])*\"?|'(?:\\\\.|[^'\\\\\\n])*'?))",
  "(\\b\\d+(?:\\.\\d+)?(?:[eE][+-]?\\d+)?\\b)",
  "([A-Za-z_\\u00C0-\\u017F][\\w\\u00C0-\\u017F]*)",
  "(\\s+)",
  "([^\\s\\w])",
  "([\\s\\S])", // filet de sécurité : aucun caractère ne doit être perdu
].join("|"), "g");

function echapper(texte) {
  return texte.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function colorer(code) {
  let html = "";
  let precedent = "";
  MOTIF.lastIndex = 0;
  let trouve;
  while ((trouve = MOTIF.exec(code)) !== null) {
    if (trouve[0] === "") { MOTIF.lastIndex++; continue; }
    const [texte, commentaire, chaine, nombre, nom] = trouve;
    const sur = echapper(texte);
    if (commentaire) html += `<span class="c-com">${sur}</span>`;
    else if (chaine) html += `<span class="c-str">${sur}</span>`;
    else if (nombre) html += `<span class="c-num">${sur}</span>`;
    else if (nom) {
      if (MOTS_CLES.has(nom)) html += `<span class="c-kw">${sur}</span>`;
      else if (precedent === "def" || precedent === "class") html += `<span class="c-fn">${sur}</span>`;
      else if (INTEGRES.has(nom)) html += `<span class="c-bi">${sur}</span>`;
      else html += sur;
    } else html += sur;
    if (!/^\s+$/.test(texte)) precedent = texte;
  }
  return html;
}
