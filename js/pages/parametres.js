// Page 8 — Paramètres : identité, éditeur, exécution, sauvegarde, moteur Python, sécurité.

import { el, carte, toast, confirmer, telecharger, copierTexte, modale } from "../interface.js";
import { stockage } from "../stockage.js";
import { moteur } from "../moteur_python.js";

export function afficher(vue, { etat, rafraichir }) {
  const reglages = etat.reglages;
  const sauver = (message = "Paramètres enregistrés.") => { stockage.sauver(); toast(message, { type: "succes", duree: 1800 }); };

  vue.append(el("header", { class: "entete-page" },
    el("p", { class: "surtitre", text: "CONFIGURATION" }),
    el("h1", { text: "Paramètres" })));

  // Identité ------------------------------------------------------------------
  const champNom = el("input", { type: "text", class: "champ", value: etat.agent.nom, maxlength: "30", placeholder: "Ton nom de code" });
  const identite = carte("Identité de l'agent",
    el("label", { class: "etiquette", text: "Nom de code" }), champNom,
    el("div", { class: "actions" }, el("button", { class: "bouton bouton-principal", type: "button", text: "Enregistrer",
      on: { click: () => { etat.agent.nom = champNom.value.trim(); sauver(); } } })));

  // Éditeur -------------------------------------------------------------------
  const champTaille = el("input", { type: "range", min: "12", max: "22", value: String(reglages.tailleEditeur), class: "curseur",
    on: { input: (evt) => { valeurTaille.textContent = `${evt.target.value} px`; },
      change: (evt) => { reglages.tailleEditeur = Number(evt.target.value); sauver(); } } });
  const valeurTaille = el("span", { class: "mono", text: `${reglages.tailleEditeur} px` });
  const editeur = carte("Éditeur de code",
    el("label", { class: "etiquette", text: "Taille du texte" }), el("div", { class: "ligne-champs" }, champTaille, valeurTaille),
    interrupteur("Coloration syntaxique", reglages.coloration, (v) => { reglages.coloration = v; sauver(); }),
    el("label", { class: "etiquette", text: "Barre de symboles (utile sur iPad sans clavier)" }),
    el("select", { class: "champ", on: { change: (evt) => { reglages.barreSymboles = evt.target.value; sauver(); } } },
      [["auto", "Automatique (écrans tactiles)"], ["toujours", "Toujours afficher"], ["jamais", "Jamais"]]
        .map(([id, nom]) => el("option", { value: id, selected: reglages.barreSymboles === id, text: nom }))),
    el("p", { class: "texte-doux petit", text: "Sur iPad : désactive « Ponctuation intelligente » (Réglages > Général > Clavier) pour éviter les guillemets courbes. L'éditeur les corrige aussi automatiquement." }));

  // Exécution et progression --------------------------------------------------
  const champDelai = el("input", { type: "range", min: "1", max: "10", value: String(reglages.delai), class: "curseur",
    on: { input: (evt) => { valeurDelai.textContent = `${evt.target.value} s`; },
      change: (evt) => { reglages.delai = Number(evt.target.value); sauver(); } } });
  const valeurDelai = el("span", { class: "mono", text: `${reglages.delai} s` });
  const execution = carte("Exécution et progression",
    el("label", { class: "etiquette", text: "Durée maximale d'exécution d'un programme" }),
    el("div", { class: "ligne-champs" }, champDelai, valeurDelai),
    interrupteur("Mode libre : toutes les missions débloquées", reglages.modeLibre, (v) => { reglages.modeLibre = v; sauver(); },
      "Pratique pour suivre l'ordre de ton propre cours."),
    interrupteur("Animations", reglages.animations, (v) => {
      reglages.animations = v; document.body.classList.toggle("sans-animations", !v); sauver();
    }));

  // Sauvegarde ----------------------------------------------------------------
  const fichier = el("input", { type: "file", accept: "application/json,.json", style: { display: "none" },
    on: { change: async (evt) => {
      const [f] = evt.target.files;
      if (!f) return;
      importer(await f.text());
      evt.target.value = "";
    } } });
  const importer = (texte) => {
    try {
      stockage.importer(texte);
      toast("Progression importée.", { type: "succes" });
      rafraichir();
    } catch (erreur) {
      toast(erreur.message, { type: "alerte", titre: "Import impossible" });
    }
  };
  const sauvegarde = carte("Sauvegarde de la progression",
    el("p", { class: "texte-doux", text: stockage.persistant
      ? "Ta progression est enregistrée automatiquement dans ce navigateur, sur cet appareil uniquement."
      : "⚠ Le stockage local est indisponible (navigation privée ?) : la progression sera perdue à la fermeture." }),
    el("p", { class: "texte-doux petit", text: "Exporte régulièrement une copie : c'est aussi le moyen de passer ta progression de l'ordinateur à l'iPad (et inversement)." }),
    el("div", { class: "actions" },
      el("button", { class: "bouton bouton-principal", type: "button", text: "Exporter (fichier)",
        on: { click: () => telecharger(`agent-python-sauvegarde-${new Date().toISOString().slice(0, 10)}.json`, stockage.exporter()) } }),
      el("button", { class: "bouton", type: "button", text: "Copier la sauvegarde",
        on: { click: async () => toast(await copierTexte(stockage.exporter()) ? "Sauvegarde copiée dans le presse-papiers." : "Copie impossible.", { type: "info" }) } }),
      el("button", { class: "bouton", type: "button", text: "Importer un fichier", on: { click: () => fichier.click() } }),
      el("button", { class: "bouton", type: "button", text: "Coller une sauvegarde",
        on: { click: async () => {
          const zone = el("textarea", { class: "champ mono", rows: "8", placeholder: "Colle ici le contenu de la sauvegarde" });
          const texte = await modale({ titre: "Importer une sauvegarde", contenu: zone,
            actions: [{ texte: "Annuler", valeur: null, classe: "bouton-discret" }, { texte: "Importer", valeur: () => zone.value, classe: "bouton-principal" }] });
          if (texte) importer(texte);
        } } }),
      fichier),
    el("div", { class: "zone-danger" },
      el("button", { class: "bouton bouton-danger", type: "button", text: "Réinitialiser toute la progression",
        on: { click: async () => {
          const ok = await confirmer({ titre: "Tout effacer ?", danger: true, ok: "Tout effacer",
            message: "XP, missions, badges, erreurs et missions générées seront supprimés définitivement. Pense à exporter une sauvegarde avant." });
          if (ok) { stockage.reinitialiser(); toast("Progression réinitialisée."); rafraichir(); }
        } } })));

  // Moteur Python -------------------------------------------------------------
  const etatMoteur = el("p", { class: "mono" });
  const majMoteur = () => {
    const source = moteur.info?.source === "locale" ? "copie locale (vendor/pyodide)" : "cache du navigateur / CDN";
    etatMoteur.textContent = moteur.etat === "pret"
      ? `✓ Prêt — Python ${moteur.info.python} — source : ${source}` : `${moteur.etat} — ${moteur.message}`;
  };
  const retirer = moteur.ecouter(majMoteur);
  const moteurCarte = carte("Moteur Python",
    etatMoteur,
    el("p", { class: "texte-doux petit", text: "Python tourne directement dans le navigateur grâce à Pyodide (WebAssembly). Après le premier chargement, il est conservé en cache et fonctionne hors ligne." }),
    el("div", { class: "actions" },
      el("button", { class: "bouton", type: "button", text: "Tester le moteur",
        on: { click: async () => {
          try {
            const r = await moteur.appeler("executer", { code: "print(sum(range(10)))", delai: 2 }, 10);
            toast(r.sortie.trim() === "45" ? "Le moteur fonctionne correctement." : "Résultat inattendu.", { type: "succes" });
          } catch (erreur) { toast(erreur.message, { type: "alerte" }); }
        } } }),
      el("button", { class: "bouton bouton-discret", type: "button", text: "Redémarrer le moteur",
        on: { click: () => moteur.redemarrer("Redémarrage manuel").catch(() => {}) } })));

  const securite = carte("Sécurité et confidentialité",
    el("ul", { class: "liste-simple" },
      el("li", { text: "Aucune API externe, aucun compte, aucune donnée envoyée : tout reste sur cet appareil." }),
      el("li", { text: "Ton code s'exécute dans un fil séparé (Web Worker) isolé de la page, sans accès à tes fichiers." }),
      el("li", { text: "Une limite de temps arrête les boucles infinies ; seuls certains modules peuvent être importés." }),
      el("li", { text: "Cette protection n'est pas absolue : n'exécute que ton propre code, jamais un code reçu d'inconnus." })));

  vue.append(el("div", { class: "grille-deux" },
    el("div", { class: "colonne" }, identite, editeur, execution),
    el("div", { class: "colonne" }, sauvegarde, moteurCarte, securite)));
  return retirer;
}

function interrupteur(libelle, valeur, surChange, aide = "") {
  const caseACocher = el("input", { type: "checkbox", role: "switch", checked: valeur, on: { change: (evt) => surChange(evt.target.checked) } });
  return el("label", { class: "interrupteur" }, caseACocher, el("span", { class: "interrupteur-curseur", "aria-hidden": "true" }),
    el("span", {}, el("span", { text: libelle }), aide ? el("span", { class: "texte-doux petit bloc", text: aide }) : null));
}
