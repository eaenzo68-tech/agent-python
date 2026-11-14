// Web Worker : charge Python (Pyodide) puis exécute les demandes de l'interface.
// Ce fichier tourne dans un fil séparé : il n'a accès ni à la page, ni à tes fichiers.

const VERSION_PYODIDE = "0.27.7"; // Python 3.12
const SOURCE_CDN = `https://cdn.jsdelivr.net/pyodide/v${VERSION_PYODIDE}/full/`;
const SOURCE_LOCALE = new URL("../vendor/pyodide/", self.location.href).href;
const DOSSIER_PYTHON = "/home/pyodide/agentpy";
const FICHIERS_PYTHON = [
  "__init__.py", "api.py", "code_runner.py", "code_quality.py", "error_explainer.py",
  "hint_engine.py", "mission_generator.py", "test_engine.py",
];

let api = null;

function signaler(texte) {
  self.postMessage({ type: "progression", texte });
}

/** Utilise la copie locale de Pyodide si elle existe (outils/telecharger_pyodide.py), sinon le CDN. */
async function choisirSource() {
  try {
    const reponse = await fetch(SOURCE_LOCALE + "pyodide.js", { method: "HEAD", cache: "no-store" });
    if (reponse.ok) return SOURCE_LOCALE;
  } catch {
    // pas de copie locale
  }
  return SOURCE_CDN;
}

async function demarrer() {
  const source = await choisirSource();
  signaler(source === SOURCE_LOCALE ? "Chargement de Python (copie locale)…" : "Chargement de Python…");
  importScripts(source + "pyodide.js");
  const pyodide = await loadPyodide({ indexURL: source, stdout: () => {}, stderr: () => {} });

  signaler("Installation du moteur pédagogique…");
  pyodide.FS.mkdirTree(`${DOSSIER_PYTHON}/core`);
  for (const nom of FICHIERS_PYTHON) {
    const reponse = await fetch(new URL(`../core/${nom}`, self.location.href), { cache: "no-cache" });
    if (!reponse.ok) throw new Error(`Fichier introuvable : core/${nom}`);
    pyodide.FS.writeFile(`${DOSSIER_PYTHON}/core/${nom}`, await reponse.text());
  }
  pyodide.runPython(`import sys\nsys.path.insert(0, ${JSON.stringify(DOSSIER_PYTHON)})`);
  api = pyodide.pyimport("core.api");
  self.postMessage({
    type: "pret",
    python: api.version_python(),
    source: source === SOURCE_LOCALE ? "locale" : "cdn",
  });
}

self.onmessage = (evt) => {
  const { id, action, charge } = evt.data;
  if (!api) {
    self.postMessage({ type: "reponse", id, ok: false, erreur: "Le moteur Python n'est pas encore prêt." });
    return;
  }
  try {
    const texte = api.traiter(action, charge);
    self.postMessage({ type: "reponse", id, ok: true, resultat: JSON.parse(texte) });
  } catch (erreur) {
    self.postMessage({ type: "reponse", id, ok: false, erreur: String(erreur && erreur.message || erreur) });
  }
};

demarrer().catch((erreur) => {
  const horsLigne = typeof navigator !== "undefined" && navigator.onLine === false;
  self.postMessage({
    type: "erreur_demarrage",
    texte: horsLigne
      ? "Impossible de charger Python : l'appareil est hors ligne et le moteur n'a pas encore été mis en cache. "
        + "Connecte-toi une fois à Internet (ou installe la copie locale, voir README)."
      : `Impossible de charger Python : ${erreur && erreur.message ? erreur.message : erreur}`,
  });
});
