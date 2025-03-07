// script.js

/*
============================================================
VARIABLES GLOBALES
============================================================
*/

let imageData = []; // Données des images
let videoData = []; // Données des vidéos

/*
============================================================
FONCTIONS UTILITAIRES
============================================================
*/

function isVideo(path) {
    const videoExtensions = ['.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv'];
    return videoExtensions.some(extension => path.toLowerCase().endsWith(extension));
}

// Initialisation des données
function initializeData() {
    const tableRows = document.querySelectorAll('#mainTable tbody tr');
    tableRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const src = cells[0]?.textContent || '';
        const alt = cells[1]?.textContent || '';

        if (src) {
            if (isVideo(src)) {
                videoData.push({ src, alt });
            } else {
                imageData.push({ src, alt });
            }
        }
    });
    //console.log("Data is ready for view change!");
}

/*
============================================================
FONCTIONS POUR LES PREVIEWS
============================================================
*/

function createPreviewBubble(content) { // Fonction pour afficher une bulle de preview
    const bubble = document.createElement('div');
    bubble.classList.add('position-absolute', 'bg-light', 'border', 'border-secondary', 'rounded', 'p-2', 'shadow-lg', 'text-center', 'w-25');
    
    bubble.innerHTML = content;
    
    document.body.appendChild(bubble);

    return bubble;
}

// Fonction pour décaler une bulle par rapport à la souris
function positionPreviewBubble(bubble, x, y) {
    const offset = 10;
    const scrollOffset = window.scrollY; // Offset du scrolling à prendre en compte pour les tables très grande
    // TODO : Touver une alternative à style pour ne pas avoir de style "inline"
    bubble.style.left = `${x + offset}px`;
    bubble.style.top = `${y + offset + scrollOffset}px`;
}

// Ajouter les previews aux images
function attachPreviewListeners() {
    const rows = document.querySelectorAll('#mainTable tbody tr');
    rows.forEach((row, index) => {
        // Obtenir le chemin et le alt à partir de la table
        const cells = row.querySelectorAll('td');
        const src = cells[0]?.textContent || '';
        const alt = cells[1]?.textContent || '';
        
        if (index === 0 || !src ) { // Sauter les lignes sans image
            return;
        }

        row.addEventListener('mousedown', function (event) {
            let bubble;
            if (isVideo(src)) {
                const videoPreview = `<video muted class="w-100"><source src="${src}" type="video/${src.slice(-3)}">Your browser does not support the video tag.</video>`;               
                bubble = createPreviewBubble(videoPreview);
            } else {
                bubble = createPreviewBubble(`<img src="${src}" alt="${alt}" class="d-block w-100" />`);
            }
            positionPreviewBubble(bubble, event.clientX, event.clientY);

            // Handling de moveEvent pour bouger l'image avec la souris!
            const moveHandler = (moveEvent) => {
                positionPreviewBubble(bubble, moveEvent.clientX, moveEvent.clientY);
            };

            // Au relâchement
            const upHandler = () => {
                bubble.remove();
                window.removeEventListener('mousemove', moveHandler);
                window.removeEventListener('mouseup', upHandler);
            };

            //Event listeners
            window.addEventListener('mousemove', moveHandler);
            window.addEventListener('mouseup', upHandler);
        });
    });
    //console.log("Ready to preview images!");
}

/*
============================================================
FONCTIONS POUR LES CHANGEMENTS DE VUE
============================================================
*/

// Fonction pour retourner à la vue table
function showTableView() {
    const table = document.createElement('table');
    table.classList.add('table', 'table-striped');
    table.id = 'mainTable';

    // Section header de la table
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    const headerCell1 = document.createElement('th');
    headerCell1.textContent = 'ressource';
    const headerCell2 = document.createElement('th');
    headerCell2.textContent = 'alt';
    headerRow.appendChild(headerCell1);
    headerRow.appendChild(headerCell2);
    thead.appendChild(headerRow);
    
    table.appendChild(thead);

    // Corps de la table
    const tbody = document.createElement('tbody');
    
    const hiddenRow = document.createElement('tr'); // Rangée cachée pour inverser les stripes de la table
    hiddenRow.classList.add('d-none');
    tbody.appendChild(hiddenRow);

    imageData.forEach(image => {
        const row = document.createElement('tr');
        const cell1 = document.createElement('td');
        cell1.textContent = image.src;
        const cell2 = document.createElement('td');
        cell2.textContent = image.alt || '';
        row.appendChild(cell1);
        row.appendChild(cell2);
        tbody.appendChild(row);
    });

    // Ajouts des vidéos
    videoData.forEach(video => {
        const row = document.createElement('tr');
        const cell1 = document.createElement('td');
        cell1.textContent = video.src;
        const cell2 = document.createElement('td');
        cell2.textContent = video.alt || '';
        row.appendChild(cell1);
        row.appendChild(cell2);
        tbody.appendChild(row);
    });

    table.appendChild(tbody);

    // Boutons Carrousel et Gallerie
    const buttonContainer = document.getElementById('buttonContainer');

    const col1 = document.createElement('div');
    col1.classList.add('col-md-6', 'text-xs-start', 'text-md-end');
    const carouselButton = document.createElement('button');
    carouselButton.classList.add('btn', 'btn-primary', 'mx-5', 'w-25');
    carouselButton.id = 'carouselButton';
    carouselButton.textContent = 'Carrousel';
    col1.appendChild(carouselButton);

    const col2 = document.createElement('div');
    col2.classList.add('col-md-6', 'text-xs-start');
    const galleryButton = document.createElement('button');
    galleryButton.classList.add('btn', 'btn-primary', 'mx-5', 'w-25');
    galleryButton.id = 'galleryButton';
    galleryButton.textContent = 'Gallerie';
    col2.appendChild(galleryButton);    

    // "wipe" du contenu existant et ajout du contenu de la table
    document.getElementById('mainContent').innerHTML = '';
    document.getElementById('mainContent').appendChild(table);

    // "wipe" des boutons existants et ajout des boutons Carrousel et Gallerie
    buttonContainer.innerHTML = '';
    buttonContainer.appendChild(col1);
    buttonContainer.appendChild(col2);

    // Event listeners pour les boutons
    carouselButton.addEventListener('click', showCarousel);
    galleryButton.addEventListener('click', showGallery);

    attachPreviewListeners();
}

// Fonction pour ajouter le bouton "Back"
function createBackButton() {
    const backButton = document.createElement('button');
    backButton.classList.add('btn', 'btn-primary', 'w-25');
    backButton.id = 'backButton';
    backButton.textContent = 'Back';
    
    const buttonContainer = document.getElementById('buttonContainer');
    buttonContainer.innerHTML = '';
    
    buttonContainer.appendChild(backButton); 
    
    return backButton;
}

// Fonction pour afficher la vue carrousel
// https://getbootstrap.com/docs/5.0/components/carousel/
function showCarousel() {
    // Container pour le carrousel
    const carouselContainer = document.createElement('div');
    carouselContainer.id = 'imageCarousel';
    carouselContainer.classList.add('carousel', 'slide');
    carouselContainer.setAttribute('data-bs-ride', 'carousel');

    // Indicateurs
    const carouselIndicators = document.createElement('ol');
    carouselIndicators.classList.add('carousel-indicators');
    
    // Inner
    const carouselInner = document.createElement('div');
    carouselInner.classList.add('carousel-inner');

    
    imageData.forEach((image, index) => {
        const indicatorButton = document.createElement('button');
        indicatorButton.setAttribute('type', 'button');
        indicatorButton.setAttribute('data-bs-target', '#imageCarousel');
        indicatorButton.setAttribute('data-bs-slide-to', index);
        indicatorButton.setAttribute('aria-current', index === 0 ? 'true' : 'false');
        indicatorButton.setAttribute('aria-label', 'Slide ' + (index + 1));
        indicatorButton.classList.add('carousel-indicator');
        if (index === 0) {
            indicatorButton.classList.add('active');
        }
        carouselIndicators.appendChild(indicatorButton);

        // Item du carrousel
        const carouselItem = document.createElement('div');
        carouselItem.classList.add('carousel-item');
        if (index === 0) { 
            carouselItem.classList.add('active');
        }
            
        // Image
        const img = document.createElement('img');
        img.src = image.src;
        img.classList.add('d-block', 'w-100');
        img.alt = image.alt || '';

        // Caption de l'image
        const caption = document.createElement('div');
        caption.classList.add('carousel-caption', 'd-none', 'd-md-block');

        const captionText = document.createElement('h5');
        captionText.textContent = `Ressource ${index + 1}`; // Index + 1 pour le numéro de ressource
        caption.appendChild(captionText);

        // Si alt
        if (image.alt) {
            const altText = document.createElement('p');
            altText.textContent = image.alt;
            caption.appendChild(altText);
        }

        carouselItem.appendChild(img);
        carouselItem.appendChild(caption);
        carouselInner.appendChild(carouselItem);
    });

    carouselContainer.appendChild(carouselIndicators);
    carouselContainer.appendChild(carouselInner);

    // Contrôles du carrousel
    const prevButton = document.createElement('button');
    prevButton.classList.add('carousel-control-prev');
    prevButton.setAttribute('type', 'button');
    prevButton.setAttribute('data-bs-target', '#imageCarousel');
    prevButton.setAttribute('data-bs-slide', 'prev');

    const prevIcon = document.createElement('span');
    prevIcon.classList.add('carousel-control-prev-icon');
    prevIcon.setAttribute('aria-hidden', 'true');
    prevButton.appendChild(prevIcon);
    const prevText = document.createElement('span');
    prevText.classList.add('visually-hidden');
    prevText.textContent = 'Previous';
    prevButton.appendChild(prevText);

    const nextButton = document.createElement('button');
    nextButton.classList.add('carousel-control-next');
    nextButton.setAttribute('type', 'button');
    nextButton.setAttribute('data-bs-target', '#imageCarousel');
    nextButton.setAttribute('data-bs-slide', 'next');

    const nextIcon = document.createElement('span');
    nextIcon.classList.add('carousel-control-next-icon');
    nextIcon.setAttribute('aria-hidden', 'true');
    nextButton.appendChild(nextIcon);
    const nextText = document.createElement('span');
    nextText.classList.add('visually-hidden');
    nextText.textContent = 'Next';
    nextButton.appendChild(nextText);

    carouselContainer.appendChild(prevButton);
    carouselContainer.appendChild(nextButton);   

    // "wipe" du contenu existant et ajout du contenu du carrousel
    document.getElementById('mainContent').innerHTML = '';
    document.getElementById('mainContent').appendChild(carouselContainer);

    // Bouton "back"
    createBackButton();
    // Event listener pour le bouton "back"
    const backButton = document.getElementById('backButton');
    backButton.addEventListener('click', showTableView);
}

// Afficher la vue Gallerie
function showGallery() {
    // Container pour la gallerie
    const galleryContainer = document.createElement('div');
    galleryContainer.classList.add('row', 'row-cols-1', 'row-cols-md-3', 'g-4');

    // Créer les items de la gallerie
    imageData.forEach(image => {
        const col = document.createElement('div');
        col.classList.add('col');

        // Créer l'image avec coins arrondis
        const img = document.createElement('img');
        img.src = image.src;
        img.classList.add('img-fluid', 'rounded');
        img.alt = image.alt || '';

        col.appendChild(img);
        galleryContainer.appendChild(col);
    });
 

    // "wipe" du contenu existant et ajout du contenu de la gallerie
    document.getElementById('mainContent').innerHTML = '';
    document.getElementById('mainContent').appendChild(galleryContainer);

    // Bouton "back"
    createBackButton();
    // Event listener pour le bouton "back"
    const backButton = document.getElementById('backButton');
    backButton.addEventListener('click', showTableView);
}

/*
============================================================
INITIALISATION
============================================================
*/

document.addEventListener('DOMContentLoaded', function () {
    // Charger les données des images et vidéos
    initializeData();
    
    // Event listeners pour les boutons
    document.getElementById('carouselButton').addEventListener('click', showCarousel);
    document.getElementById('galleryButton').addEventListener('click', showGallery);
    //console.log("Buttons are ready!");

    // Event listeners pour les previews
    attachPreviewListeners();
});