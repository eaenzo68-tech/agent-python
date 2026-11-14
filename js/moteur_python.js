// Pont entre l'interface et le moteur Python (qui tourne dans un Web Worker).
//
// Pourquoi un Worker ? Le code de l'agent s'exécute dans un fil séparé :
// - l'interface reste fluide pendant l'exécution ;
// - si le programme reste bloqué (boucle infinie « dure »), on peut ARRÊTER
//   complètement le Worker avec terminate(), puis en relancer un neuf.
// C'est l'équivalent, dans un navigateur, d'un « processus séparé ».

const URL_WORKER = "worker/moteur_python.js";
const DELAI_CHARGEMENT = 180_000; // premier lancement : téléchargement de Python (~10 Mo)

export class DelaiDepasse extends Error {
  constructor(secondes) {
    super(`Le programme ne répond plus après ${secondes} s : il a été arrêté.`);
    this.name = "DelaiDepasse";
    this.secondes = secondes;
  }
}

class MoteurPython {
  constructor() {
    this.worker = null;
    this.etat = "arret";        // arret | chargement | pret | erreur
    this.message = "";
    this.info = null;           // { python, source }
    this.attentes = new Map();  // id -> { resoudre, rejeter, minuterie }
    this.compteur = 0;
    this.ecouteurs = new Set();
    this.pret = null;
  }

  ecouter(fonction) {
    this.ecouteurs.add(fonction);
    fonction(this);
    return () => this.ecouteurs.delete(fonction);
  }

  _changer(etat, message = "") {
    this.etat = etat;
    this.message = message;
    for (const ecouteur of this.ecouteurs) ecouteur(this);
  }

  demarrer() {
    if (this.worker) return this.pret;
    this._changer("chargement", "Chargement du moteur Python…");
    this.worker = new Worker(URL_WORKER);
    this.pret = new Promise((resoudre, rejeter) => {
      const minuterie = setTimeout(() => {
        this._changer("erreur", "Le moteur Python met trop de temps à se charger. Vérifie ta connexion au premier lancement.");
        rejeter(new Error(this.message));
      }, DELAI_CHARGEMENT);
      this.worker.onmessage = (evt) => {
        const msg = evt.data;
        if (msg.type === "pret") {
          clearTimeout(minuterie);
          this.info = { python: msg.python, source: msg.source };
          this._changer("pret", `Python ${msg.python}`);
          resoudre(this);
        } else if (msg.type === "progression") {
          this._changer("chargement", msg.texte);
        } else if (msg.type === "erreur_demarrage") {
          clearTimeout(minuterie);
          this._changer("erreur", msg.texte);
          rejeter(new Error(msg.texte));
        } else if (msg.type === "reponse") {
          this._repondre(msg);
        }
      };
      this.worker.onerror = (evt) => {
        clearTimeout(minuterie);
        this._changer("erreur", `Erreur du moteur : ${evt.message || "inconnue"}`);
        rejeter(new Error(this.message));
      };
    });
    this.pret.catch(() => {}); // l'erreur est affichée via l'état
    return this.pret;
  }

  _repondre(msg) {
    const attente = this.attentes.get(msg.id);
    if (!attente) return;
    clearTimeout(attente.minuterie);
    this.attentes.delete(msg.id);
    if (msg.ok) attente.resoudre(msg.resultat);
    else attente.rejeter(new Error(msg.erreur));
  }

  /** Arrête le Worker (par exemple après une boucle infinie) et en démarre un neuf. */
  redemarrer(raison = "") {
    if (this.worker) this.worker.terminate();
    this.worker = null;
    for (const attente of this.attentes.values()) {
      clearTimeout(attente.minuterie);
      attente.rejeter(raison instanceof Error ? raison : new Error(raison || "Moteur redémarré"));
    }
    this.attentes.clear();
    return this.demarrer();
  }

  /**
   * Appelle une action du moteur Python (voir core/api.py).
   * delaiMax : temps maximum (secondes) avant d'arrêter de force le Worker.
   */
  async appeler(action, charge = {}, delaiMax = 20) {
    if (!this.worker) this.demarrer();
    await this.pret;
    const id = ++this.compteur;
    return new Promise((resoudre, rejeter) => {
      const minuterie = setTimeout(() => {
        this.attentes.delete(id);
        const erreur = new DelaiDepasse(delaiMax);
        rejeter(erreur);
        this.redemarrer(erreur).catch(() => {});
      }, delaiMax * 1000);
      this.attentes.set(id, { resoudre, rejeter, minuterie });
      this.worker.postMessage({ id, action, charge: JSON.stringify(charge) });
    }).then((resultat) => {
      if (resultat && resultat.erreur_interne) {
        console.error("Erreur interne du moteur :", resultat.details || resultat.erreur_interne);
        throw new Error(resultat.erreur_interne);
      }
      return resultat;
    });
  }
}

export const moteur = new MoteurPython();
