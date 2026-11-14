// Page 2 — Nouvelle mission : générer des missions à partir du cours, ou créer la sienne.

import { el, vider, carte, toast, puce } from "../interface.js";
import { donnees, THEMES, DIFFICULTES, CONCEPTS_GENERABLES } from "../donnees.js";
import { moteur } from "../moteur_python.js";
import { stockage } from "../stockage.js";
import { genererMissions } from "../generation.js";
import { carteMission } from "../composants.js";

const NIVEAUX_DECLARES = { debutant: "Débutant", intermediaire: "Intermédiaire", a_l_aise: "À l'aise" };

export function afficher(vue, { etat }) {
  let onglet = "generer";
  vue.append(el("header", { class: "entete-page" },
    el("p", { class: "surtitre", text: "SALLE DE PLANIFICATION" }),
    el("h1", { text: "Nouvelle mission" }),
    el("p", { class: "texte-doux", text: "Transforme ton cours en missions d'entraînement, entièrement hors ligne." })));

  const ongletsZone = el("div", { class: "onglets", role: "tablist" });
  const contenu = el("div");
  vue.append(ongletsZone, contenu);

  const rendre = () => {
    vider(ongletsZone).append(
      el("button", { class: `onglet${onglet === "generer" ? " actif" : ""}`, role: "tab", type: "button", text: "Générer à partir du cours",
        on: { click: () => { onglet = "generer"; rendre(); } } }),
      el("button", { class: `onglet${onglet === "creer" ? " actif" : ""}`, role: "tab", type: "button", text: "Créer ma mission",
        on: { click: () => { onglet = "creer"; rendre(); } } }));
    vider(contenu).append(onglet === "generer" ? formulaireGeneration(etat) : formulaireCreation(etat));
  };
  rendre();
}

// ---------------------------------------------------------------------------
// Génération
// ---------------------------------------------------------------------------

function formulaireGeneration(etat) {
  const memoire = etat.formulaireGeneration || {
    themes: "", notes: "", concepts: [], niveaux: {}, nombre: 3, difficulte: "facile",
  };
  const choisis = new Set(memoire.concepts);
  const niveaux = { ...memoire.niveaux };

  const champThemes = el("input", { type: "text", class: "champ", value: memoire.themes,
    placeholder: "ex. : boucles for, listes, dictionnaires" });
  const champNotes = el("textarea", { class: "champ", rows: "6",
    placeholder: "Colle ici un extrait de tes notes de cours (texte ou code)…" });
  champNotes.value = memoire.notes;
  const resultatAnalyse = el("div", { class: "resultat-analyse" });
  const grilleConcepts = el("div", { class: "grille-concepts" });
  const champNombre = el("input", { type: "number", class: "champ champ-court", min: "1", max: "10", value: String(memoire.nombre) });
  let difficulte = memoire.difficulte;
  const selecteurDifficulte = el("div", { class: "segmente", role: "radiogroup", "aria-label": "Difficulté" });
  const zoneMissions = el("div", { class: "grille-missions" });
  const boutonGenerer = el("button", { class: "bouton bouton-principal", type: "button", text: "Générer les missions" });

  const rendreDifficulte = () => {
    vider(selecteurDifficulte).append(...Object.entries(DIFFICULTES).map(([id, nom]) => el("button", {
      type: "button", role: "radio", "aria-checked": String(difficulte === id),
      class: `segment${difficulte === id ? " actif" : ""}`, text: nom,
      on: { click: () => { difficulte = id; rendreDifficulte(); } },
    })));
  };

  const rendreConcepts = () => {
    vider(grilleConcepts);
    for (const concept of donnees.concepts) {
      const generable = CONCEPTS_GENERABLES.includes(concept.id);
      const case_ = el("input", { type: "checkbox", checked: choisis.has(concept.id), disabled: !generable,
        on: { change: (evt) => { if (evt.target.checked) choisis.add(concept.id); else choisis.delete(concept.id); rendreConcepts(); } } });
      const niveau = el("select", { class: "champ champ-mini", "aria-label": `Ton niveau en ${concept.nom}`,
        disabled: !choisis.has(concept.id),
        on: { change: (evt) => { niveaux[concept.id] = evt.target.value; } } },
      Object.entries(NIVEAUX_DECLARES).map(([id, nom]) => el("option", { value: id, selected: (niveaux[concept.id] || "intermediaire") === id, text: nom })));
      grilleConcepts.append(el("div", { class: `choix-concept${choisis.has(concept.id) ? " choisi" : ""}${generable ? "" : " indisponible"}` },
        el("label", {}, case_, el("span", { text: concept.nom })),
        generable ? niveau : el("span", { class: "texte-doux petit", text: "fiche seulement" })));
    }
  };

  const analyser = async () => {
    const texte = `${champThemes.value}\n${champNotes.value}`;
    if (!texte.trim()) { toast("Écris des thèmes ou colle tes notes d'abord.", { type: "info" }); return; }
    vider(resultatAnalyse).append(el("p", { class: "texte-doux", text: "Analyse des notes…" }));
    try {
      const { concepts } = await moteur.appeler("analyser_notes", { texte, catalogue: donnees.concepts }, 15);
      vider(resultatAnalyse);
      if (!concepts.length) {
        resultatAnalyse.append(el("p", { class: "texte-doux", text: "Aucun concept reconnu. Coche-les à la main ci-dessous." }));
        return;
      }
      resultatAnalyse.append(el("p", { text: "Concepts repérés dans ton texte :" }),
        el("div", { class: "nuage-puces" }, concepts.map((c) => puce(`${c.nom} (${c.score})`, CONCEPTS_GENERABLES.includes(c.id) ? "puce-theme" : ""))));
      for (const concept of concepts) if (CONCEPTS_GENERABLES.includes(concept.id)) choisis.add(concept.id);
      rendreConcepts();
      const nonGenerables = concepts.filter((c) => !CONCEPTS_GENERABLES.includes(c.id));
      if (nonGenerables.length) {
        resultatAnalyse.append(el("p", { class: "texte-doux petit",
          text: `Pas encore de modèle de mission pour : ${nonGenerables.map((c) => c.nom).join(", ")}. Consulte leur fiche ou crée ta propre mission.` }));
      }
    } catch (erreur) {
      vider(resultatAnalyse).append(el("p", { class: "texte-rouge", text: `Analyse impossible : ${erreur.message}` }));
    }
  };

  boutonGenerer.addEventListener("click", async () => {
    if (!choisis.size) { toast("Choisis au moins un concept à travailler.", { type: "info" }); return; }
    const nombre = Math.max(1, Math.min(10, Number(champNombre.value) || 3));
    etat.formulaireGeneration = {
      themes: champThemes.value, notes: champNotes.value.slice(0, 5000), concepts: [...choisis], niveaux, nombre, difficulte,
    };
    stockage.sauver();
    boutonGenerer.disabled = true;
    boutonGenerer.textContent = "Génération…";
    try {
      const missions = await genererMissions({ concepts: [...choisis], nombre, difficulte, niveaux });
      vider(zoneMissions).append(
        el("p", { class: "texte-doux", text: `${missions.length} mission(s) prête(s), de la plus simple à la plus difficile. Retrouve-les aussi dans le Centre d'entraînement.` }),
        ...missions.map((m) => carteMission(m, stockage.etat)));
      toast(`${missions.length} mission(s) générée(s).`, { type: "succes" });
    } catch (erreur) {
      toast(`Génération impossible : ${erreur.message}`, { type: "alerte" });
    } finally {
      boutonGenerer.disabled = false;
      boutonGenerer.textContent = "Générer les missions";
    }
  });

  rendreDifficulte();
  rendreConcepts();

  return el("div", { class: "colonne" },
    carte("1. Ton cours",
      el("label", { class: "etiquette", text: "Thèmes du cours" }), champThemes,
      el("label", { class: "etiquette", text: "Notes de cours (facultatif)" }), champNotes,
      el("div", { class: "actions" }, el("button", { class: "bouton", type: "button", text: "Analyser mes notes", on: { click: analyser } })),
      resultatAnalyse),
    carte("2. Concepts à travailler et ton niveau",
      el("p", { class: "texte-doux petit", text: "« Débutant » simplifie les missions de ce concept, « À l'aise » les rend plus exigeantes." }),
      grilleConcepts),
    carte("3. Paramètres",
      el("div", { class: "ligne-champs" },
        el("div", {}, el("label", { class: "etiquette", text: "Nombre de missions (1 à 10)" }), champNombre),
        el("div", {}, el("span", { class: "etiquette", text: "Difficulté" }), selecteurDifficulte)),
      el("div", { class: "actions" }, boutonGenerer)),
    zoneMissions);
}

// ---------------------------------------------------------------------------
// Création manuelle
// ---------------------------------------------------------------------------

function formulaireCreation() {
  const champ = (nom, attributs = {}) => el("input", { type: "text", class: "champ", name: nom, ...attributs });
  const zone = (nom, lignes, attributs = {}) => el("textarea", { class: "champ mono", name: nom, rows: String(lignes),
    spellcheck: "false", autocapitalize: "off", autocorrect: "off", ...attributs });

  const champs = {
    titre: champ("titre", { placeholder: "ex. : Opération Doublons" }),
    concept: el("select", { class: "champ", name: "concept" },
      donnees.concepts.map((c) => el("option", { value: c.id, text: c.nom }))),
    theme: el("select", { class: "champ", name: "theme" },
      Object.entries(THEMES).map(([id, nom]) => el("option", { value: id, text: nom }))),
    briefing: zone("briefing", 2, { class: "champ", placeholder: "Facultatif : l'histoire de la mission" }),
    enonce: zone("enonce", 3, { class: "champ", placeholder: "Que doit faire le programme ?" }),
    signature: champ("signature", { class: "champ mono", placeholder: "supprimer_doublons(noms)" }),
    tests: zone("tests", 4, { placeholder: "['A', 'B', 'A'] => ['A', 'B']\n[] => []" }),
    sortie_attendue: zone("sortie_attendue", 3, { placeholder: "Texte exact que le programme doit afficher" }),
    entrees: zone("entrees", 2, { placeholder: "Une valeur par ligne (si le programme utilise input())" }),
    code_depart: zone("code_depart", 3, { placeholder: "Facultatif" }),
    solution: zone("solution", 5, { placeholder: "Facultatif mais conseillé : les tests seront vérifiés avec ta solution" }),
    indice1: champ("indice1", { placeholder: "Indice 1 (facultatif)" }),
    indice2: champ("indice2", { placeholder: "Indice 2 (facultatif)" }),
    indice3: champ("indice3", { placeholder: "Indice 3 (facultatif)" }),
    explication: zone("explication", 2, { class: "champ", placeholder: "Facultatif : ce qu'il faut retenir" }),
  };
  let mode = "fonction";
  const zoneMode = el("div");
  const erreurs = el("div", { class: "erreurs-formulaire", "aria-live": "polite" });
  const selecteurMode = el("div", { class: "segmente", role: "radiogroup" });
  const bloc = (titre, ...enfants) => el("div", { class: "bloc-champ" }, el("label", { class: "etiquette", text: titre }), ...enfants);

  const rendreMode = () => {
    vider(selecteurMode).append(
      el("button", { type: "button", class: `segment${mode === "fonction" ? " actif" : ""}`, text: "Écrire une fonction",
        on: { click: () => { mode = "fonction"; rendreMode(); } } }),
      el("button", { type: "button", class: `segment${mode === "programme" ? " actif" : ""}`, text: "Écrire un programme",
        on: { click: () => { mode = "programme"; rendreMode(); } } }));
    vider(zoneMode).append(...(mode === "fonction" ? [
      bloc("Signature de la fonction", champs.signature),
      bloc("Tests (une ligne par test : arguments => résultat attendu)", champs.tests,
        el("p", { class: "texte-doux petit", text: "Écris les valeurs comme en Python : textes entre guillemets, listes entre crochets. Plusieurs arguments : 5, 3 => 8" })),
    ] : [
      bloc("Sortie attendue", champs.sortie_attendue),
      bloc("Entrées (facultatif)", champs.entrees),
    ]));
  };
  rendreMode();

  const creer = async () => {
    const formulaire = {
      identifiant: Date.now().toString(36),
      titre: champs.titre.value, concept: champs.concept.value, theme: champs.theme.value,
      briefing: champs.briefing.value, enonce: champs.enonce.value,
      signature: mode === "fonction" ? champs.signature.value : "",
      tests: champs.tests.value, sortie_attendue: champs.sortie_attendue.value, entrees: champs.entrees.value,
      code_depart: champs.code_depart.value, solution: champs.solution.value,
      indices: [champs.indice1.value, champs.indice2.value, champs.indice3.value],
      explication: champs.explication.value,
    };
    vider(erreurs);
    try {
      const reponse = await moteur.appeler("creer_mission", { formulaire }, 20);
      if (!reponse.ok) {
        erreurs.append(el("p", { text: "La mission n'a pas pu être créée :" }),
          el("ul", {}, reponse.erreurs.map((e) => el("li", { text: e }))));
        return;
      }
      const mission = { ...reponse.mission, creeLe: new Date().toISOString() };
      stockage.etat.missionsPerso[mission.id] = mission;
      stockage.sauver();
      toast("Mission créée et ajoutée au Centre d'entraînement.", { type: "succes" });
      location.hash = `#mission-${mission.id}`;
    } catch (erreur) {
      erreurs.append(el("p", { text: `Erreur : ${erreur.message}` }));
    }
  };

  return el("div", { class: "colonne" },
    carte("Créer une mission à partir d'un sujet de cours",
      el("p", { class: "texte-doux", text: "Tu deviens l'instructeur : décris la mission, ajoute des tests, et l'application la vérifie automatiquement." }),
      el("div", { class: "ligne-champs" }, bloc("Titre", champs.titre), bloc("Sujet de cours (concept)", champs.concept), bloc("Thème", champs.theme)),
      bloc("Briefing", champs.briefing),
      bloc("Énoncé", champs.enonce),
      el("div", { class: "bloc-champ" }, el("span", { class: "etiquette", text: "Type de mission" }), selecteurMode),
      zoneMode,
      bloc("Code de départ", champs.code_depart),
      bloc("Solution de référence", champs.solution),
      bloc("Indices progressifs", champs.indice1, champs.indice2, champs.indice3,
        el("p", { class: "texte-doux petit", text: "Laissés vides, des indices génériques sur le concept choisi sont utilisés." })),
      bloc("Explication", champs.explication),
      erreurs,
      el("div", { class: "actions" }, el("button", { class: "bouton bouton-principal", type: "button", text: "Créer la mission", on: { click: creer } }))));
}

