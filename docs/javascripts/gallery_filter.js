
document.addEventListener('DOMContentLoaded', function() {
    const keywordFiltersContainer = document.getElementById('keyword-filters');
    const galleryItems = document.querySelectorAll('.gallery-item');
    const applyButton = document.getElementById('apply-filters'); 
    const resetButton = document.getElementById('reset-filters');

    if (!keywordFiltersContainer || !galleryItems.length || !applyButton || !resetButton) {
        console.warn("Certains éléments nécessaires au filtrage (conteneur, images, boutons) sont manquants. Le filtrage ne fonctionnera pas.");
        return; 
    }

    // Fonction récursive pour obtenir tous les slugs descendants d'une checkbox
    function getAllDescendantSlugs(checkbox) {
        const slugs = new Set();
        slugs.add(checkbox.value); // Ajouter le slug de la checkbox actuelle

        const parentGroup = checkbox.closest('.filter-group');
        if (parentGroup) {
            const childrenContainer = parentGroup.querySelector('.children-container');
            if (childrenContainer) {
                childrenContainer.querySelectorAll('.keyword-checkbox').forEach(childCheckbox => {
                    // Récursion pour collecter les slugs des enfants
                    getAllDescendantSlugs(childCheckbox).forEach(slug => slugs.add(slug));
                });
            }
        }
        return slugs;
    }

    // Gestion du dépliage/repliage des catégories de filtres
    keywordFiltersContainer.querySelectorAll('.keyword-toggle').forEach(toggleLabel => {
        const toggleIcon = toggleLabel.querySelector('.toggle-icon');
        const checkbox = toggleLabel.querySelector('.keyword-checkbox');

        if (toggleIcon) {
            toggleIcon.addEventListener('click', function(event) {
                event.stopPropagation(); // Empêche le clic de cocher la checkbox parente
                const parentGroup = this.closest('.filter-group');
                const childrenContainer = parentGroup.querySelector('.children-container');
                if (childrenContainer) {
                    if (childrenContainer.style.display === 'none' || childrenContainer.style.display === '') {
                        childrenContainer.style.display = 'block';
                        this.classList.add('expanded'); // Ajoute une classe pour changer l'icône
                    } else {
                        childrenContainer.style.display = 'none';
                        this.classList.remove('expanded'); // Retire la classe
                    }
                }
            });
        }

        // Gérer le clic sur la checkbox elle-même pour la propagation (parent -> enfants)
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                const parentGroup = this.closest('.filter-group');
                const childrenCheckboxes = parentGroup.querySelectorAll('.children-container .keyword-checkbox');
                childrenCheckboxes.forEach(childCheckbox => {
                    childCheckbox.checked = this.checked;
                });
            });
        }
    });

    // Fonction pour appliquer les filtres
    function applyFilters() {
        const selectedKeywords = new Set();
        let hasFilters = false;

        keywordFiltersContainer.querySelectorAll('.keyword-checkbox:checked').forEach(checkbox => {
            hasFilters = true;
            // Si la checkbox a des enfants (c'est une catégorie), inclure tous les slugs des descendants
            const parentGroup = checkbox.closest('.filter-group');
            if (parentGroup && parentGroup.querySelector('.children-container')) {
                getAllDescendantSlugs(checkbox).forEach(slug => selectedKeywords.add(slug));
            } else {
                selectedKeywords.add(checkbox.value);
            }
        });
        
        galleryItems.forEach(item => {
            const itemKeywords = item.dataset.keywords ? item.dataset.keywords.split(' ') : [];
            let isVisible = false;

            if (!hasFilters) {
                isVisible = true; // Si aucun filtre n'est sélectionné, tout est visible
            } else {
                // Vérifier si la photo correspond à AU MOINS UN des mots-clés sélectionnés
                for (const selectedKw of selectedKeywords) {
                    if (itemKeywords.includes(selectedKw)) {
                        isVisible = true;
                        break; 
                    }
                }
            }
            item.style.display = isVisible ? 'block' : 'none'; 
        });
    }

    // Attacher l'écouteur d'événements au bouton "Appliquer les filtres"
    applyButton.addEventListener('click', applyFilters);

    // Attacher l'écouteur d'événements au bouton de réinitialisation
    resetButton.addEventListener('click', function() {
        keywordFiltersContainer.querySelectorAll('.keyword-checkbox').forEach(checkbox => {
            checkbox.checked = false; // Décocher toutes les checkboxes
        });
        // Replier toutes les catégories
        keywordFiltersContainer.querySelectorAll('.children-container').forEach(container => {
            container.style.display = 'none';
        });
        keywordFiltersContainer.querySelectorAll('.toggle-icon').forEach(icon => {
            icon.classList.remove('expanded');
        });
        applyFilters(); // Réappliquer les filtres pour tout afficher
    });

    // Appliquer les filtres une fois au chargement initial
    applyFilters();
});
