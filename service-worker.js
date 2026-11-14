// Service worker : rend l'application utilisable HORS LIGNE.
//
// - Fichiers de l'application : « réseau d'abord » (pour voir tes modifications),
//   avec repli sur le cache quand il n'y a pas de connexion.
// - Moteur Python (Pyodide, ~10 Mo) : « cache d'abord », téléchargé une seule fois.
//
// Le navigateur n'active un service worker qu'en https:// ou sur localhost.

const VERSION = "agent-python-v1";
const CACHE_APP = `${VERSION}-app`;
const CACHE_PYTHON = "agent-python-pyodide-0.27.7";

const FICHIERS_APP = [
  "./", "./index.html", "./manifest.webmanifest",
  "./assets/styles.css", "./assets/icone.svg", "./assets/icone-180.png", "./assets/icone-192.png", "./assets/icone-512.png",
  "./data/missions.json", "./data/concepts.json", "./data/badges.json",
  "./js/app.js", "./js/coloration.js", "./js/composants.js", "./js/donnees.js", "./js/editeur.js",
  "./js/generation.js", "./js/interface.js", "./js/moteur_python.js", "./js/progression.js",
  "./js/stockage.js", "./js/telephone.js",
  "./js/pages/concepts.js", "./js/pages/entrainement.js", "./js/pages/erreurs.js", "./js/pages/mission.js",
  "./js/pages/nouvelle_mission.js", "./js/pages/parametres.js", "./js/pages/progression.js",
  "./js/pages/tableau_de_bord.js",
  "./worker/moteur_python.js",
  "./core/__init__.py", "./core/api.py", "./core/code_quality.py", "./core/code_runner.py",
  "./core/error_explainer.py", "./core/hint_engine.py", "./core/mission_generator.py", "./core/test_engine.py",
];

self.addEventListener("install", (evt) => {
  evt.waitUntil((async () => {
    const cache = await caches.open(CACHE_APP);
    // Un fichier manquant ne doit pas bloquer l'installation.
    await Promise.all(FICHIERS_APP.map((url) => cache.add(new Request(url, { cache: "reload" })).catch(() => {})));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (evt) => {
  evt.waitUntil((async () => {
    const noms = await caches.keys();
    await Promise.all(noms.filter((nom) => nom !== CACHE_APP && nom !== CACHE_PYTHON).map((nom) => caches.delete(nom)));
    await self.clients.claim();
  })());
});

function estPyodide(url) {
  return url.includes("/pyodide/");
}

async function cacheDabord(requete) {
  const cache = await caches.open(CACHE_PYTHON);
  const enCache = await cache.match(requete.url);
  if (enCache) return enCache;
  // Requête « cors » pour obtenir une réponse lisible et mise en cache proprement.
  const reponse = await fetch(requete.url, { mode: "cors", credentials: "omit" });
  if (reponse.ok) cache.put(requete.url, reponse.clone());
  return reponse;
}

async function reseauDabord(requete) {
  const cache = await caches.open(CACHE_APP);
  try {
    const reponse = await fetch(requete);
    if (reponse.ok && requete.method === "GET") cache.put(requete, reponse.clone());
    return reponse;
  } catch (erreur) {
    const enCache = await cache.match(requete, { ignoreSearch: true });
    if (enCache) return enCache;
    if (requete.mode === "navigate") {
      const accueil = await cache.match("./index.html");
      if (accueil) return accueil;
    }
    throw erreur;
  }
}

self.addEventListener("fetch", (evt) => {
  const requete = evt.request;
  if (requete.method !== "GET") return;
  const url = new URL(requete.url);
  if (estPyodide(url.href)) {
    evt.respondWith(cacheDabord(requete));
  } else if (url.origin === self.location.origin) {
    evt.respondWith(reseauDabord(requete));
  }
});
