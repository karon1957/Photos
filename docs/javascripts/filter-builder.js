/**
 * filter-builder.js
 *
 * Usage :
 *   > cd D:\Photo-docs\docs\javascripts
 *   > node filter-builder.js
 *
 * Cet outil scanne le dossier ../photos, 
 * génère pour chaque image un <a> dans la section .all-photos de gallery.html,
 * avec data-folder, data-date et data-keywords (vide par défaut).
 *
 * NB : Ce script suppose que vos photos sont stockées sous :
 *      D:\Photo-docs\docs\photos\<NOM_DOSSIER>\*.jpg (ou .png, .jpeg, .gif). 
 *      Il utilise le nom du sous-dossier comme valeur de data-folder,
 *      et la date de dernière modification du fichier (format YYYY-MM-DD) pour data-date.
 *      Les keywords sont initialisées à la chaîne vide. 
 *
 * Si vous voulez associer des mots-clés (data-keywords),
 * vous pouvez modifier ce script pour lire un fichier JSON cartographique
 * du genre { "IMG_0001.JPG": ["keyword1","keyword2"], … }.
 *
 * Structure attendue du projet :
 *   docs/
 *     gallery.html
 *     photos/
 *       Suisse/
 *         IMG_0001.JPG
 *         IMG_0002.JPG
 *       Thailande/
 *         IMG_0101.JPG
 *         …
 *     javascripts/
 *       filter-builder.js   <-- ici
 *       gallery.js
 *
 * A la sortie, filter-builder.js modifie gallery.html en insérant
 * AUTOMATIQUEMENT tous les <a> nécessaires dans .all-photos.
 */

const fs      = require("fs");
const path    = require("path");

// 1) Chemins relatifs basés sur l’emplacement de ce script
const repoRoot       = path.resolve(__dirname, "..");            // ...\docs
const photosDir      = path.join(repoRoot, "photos");            // ...\docs\photos
const galleryHtml    = path.join(repoRoot, "gallery.html");      // ...\docs\gallery.html

// 2) Extension des fichiers considérés comme images
const validExts = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"];

// 3) Lecture de gallery.html pour y insérer les balises <a>
let htmlContent = fs.readFileSync(galleryHtml, "utf8");

// 4) On recherchera les marqueurs suivants :
const markerStart = "<!-- ALL_PHOTOS_START -->";
const markerEnd   = "<!-- ALL_PHOTOS_END   -->";

// On vérifie qu’ils existent
if (!htmlContent.includes(markerStart) || !htmlContent.includes(markerEnd)) {
  console.error("❌ Les marqueurs ALL_PHOTOS_START / ALL_PHOTOS_END n'ont pas été trouvés dans gallery.html.");
  console.error("   Assurez-vous qu'ils sont bien présents (exactement comme dans l'exemple).");
  process.exit(1);
}

// 5) Fonction utilitaire : formate une date JS en 'YYYY-MM-DD'
function formatDateYYYYMMDD(dateObj) {
  const yyyy = dateObj.getFullYear();
  const mm   = String(dateObj.getMonth() + 1).padStart(2, "0");
  const dd   = String(dateObj.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

// 6) Fonction qui scanne récursivement un dossier (ici : un seul niveau de profondeur suffit)
function scanPhotos(baseDir) {
  // On s'attend à ce que baseDir contienne plusieurs sous-dossiers (= dossiers « Suisse », « Thailande », …).
  const dossiersHautNiveau = fs.readdirSync(baseDir, { withFileTypes: true })
                              .filter(ent => ent.isDirectory())
                              .map(ent    => ent.name);

  const resultList = []; // chaque élément sera { relPath, title, folder, date, keywords:"" }

  dossiersHautNiveau.forEach((nomDossier) => {
    const fullFolderPath = path.join(baseDir, nomDossier);
    const fichiers       = fs.readdirSync(fullFolderPath, { withFileTypes: true });

    fichiers.forEach((ent) => {
      if (ent.isFile()) {
        const ext = path.extname(ent.name).toLowerCase();
        if (validExts.includes(ext)) {
          // Chemin relatif pour le <a href="…">
          // On veut un chemin relatif depuis gallery.html : 
          //    "photos/Suisse/IMG_0001.JPG"
          const relImagePath = path.join("photos", nomDossier, ent.name).replace(/\\/g, "/");

          // Titre qu’on affiche sous la vignette (on prend le nom de fichier sans extension)
          const titleSansExt = path.basename(ent.name, ext);

          // Date de dernière modification (ou date de création si vous préférez)
          const stats    = fs.statSync(path.join(fullFolderPath, ent.name));
          const modif    = stats.mtime; // date de dernière modif
          const dateISO  = formatDateYYYYMMDD(modif);

          // Pour l’instant, keywords = chaîne vide (vous pouvez adapter si vous avez un JSON de correspondance)
          const keywordsCSV = "";

          resultList.push({
            relPath : relImagePath,
            title   : titleSansExt,
            folder  : nomDossier,
            date    : dateISO,
            keywords: keywordsCSV
          });
        }
      }
    });
  });

  return resultList;
}

// 7) Construction de toutes les balises <a> à injecter
const listePhotos = scanPhotos(photosDir);

let generatedHtml = "";

// Pour chaque photo, on génère une ligne comme :
// <a href="/photos/Suisse/IMG_0001.JPG" data-title="IMG_0001" data-folder="Suisse" data-keywords="" data-place="" data-date="2023-05-15"></a>
listePhotos.forEach((pic) => {
  generatedHtml += `    <a href="${pic.relPath}"\n`
                 + `       data-title="${pic.title}"\n`
                 + `       data-folder="${pic.folder}"\n`
                 + `       data-keywords="${pic.keywords}"\n`
                 + `       data-place=""\n`
                 + `       data-date="${pic.date}">\n`
                 + `    </a>\n`;
});

// 8) On remplace la zone située entre markerStart et markerEnd par generatedHtml
const beforeMarker = htmlContent.split(markerStart)[0] + markerStart + "\n";
const afterMarker  = "\n" + markerEnd + htmlContent.split(markerEnd)[1];

const newHtml = beforeMarker + generatedHtml + afterMarker;

// 9) Écriture dans gallery.html
fs.writeFileSync(galleryHtml, newHtml, "utf8");
console.log(`✅ gallery.html mis à jour : ${listePhotos.length} photos injectées dans .all-photos.`);
