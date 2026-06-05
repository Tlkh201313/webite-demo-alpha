/**
 * Site search — header form + search.html results.
 */
(function () {
    if (window.__nscSiteSearchInit) {
        return;
    }
    window.__nscSiteSearchInit = true;

    function assetBase() {
        const link = document.querySelector('link[href*="site-chrome.css"]');
        if (!link) {
            return "./";
        }
        const href = link.getAttribute("href") || "";
        return href.replace(/site-chrome\.css.*$/, "");
    }

    function searchPageUrl(query) {
        const base = assetBase();
        const page = `${base}search.html`;
        const trimmed = (query || "").trim();
        if (!trimmed) {
            return page;
        }
        return `${page}?q=${encodeURIComponent(trimmed)}`;
    }

    function normalize(text) {
        return (text || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }

    function scoreEntry(entry, terms) {
        const haystack = normalize(
            [entry.title, entry.label, entry.description, entry.text, entry.section].join(" ")
        );
        let score = 0;
        for (const term of terms) {
            if (!term) {
                continue;
            }
            if (normalize(entry.title).includes(term)) {
                score += 12;
            }
            if (normalize(entry.label).includes(term)) {
                score += 10;
            }
            if (normalize(entry.section).includes(term)) {
                score += 4;
            }
            if (haystack.includes(term)) {
                score += 2;
            }
        }
        return score;
    }

    function closeMobileSearch(mount, panel, toggle, form) {
        mount.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        panel.hidden = true;
        if (form.parentElement !== mount) {
            mount.appendChild(form);
        }
    }

    function setupHeaderSearch(form) {
        if (form.classList.contains("nsc-site-search--page") || form.dataset.nscSearchEnhanced === "true") {
            return;
        }
        form.dataset.nscSearchEnhanced = "true";
        form.classList.remove("hidden", "lg:flex");
        form.classList.add("nsc-site-search--header");

        const actions = form.parentElement;
        const mastheadCol = form.closest("#masthead .flex.flex-col");
        if (!actions || !mastheadCol) {
            return;
        }

        const mount = document.createElement("div");
        mount.className = "nsc-site-search__mount";
        actions.insertBefore(mount, form);
        mount.appendChild(form);

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "nsc-site-search__toggle";
        toggle.setAttribute("aria-label", "Search site");
        toggle.setAttribute("aria-expanded", "false");
        toggle.innerHTML =
            '<span class="material-symbols-outlined" aria-hidden="true">search</span>';
        mount.insertBefore(toggle, form);

        const panel = document.createElement("div");
        panel.className = "nsc-site-search__panel";
        panel.hidden = true;
        const headerRow = mastheadCol.querySelector(":scope > .flex.flex-wrap");
        if (headerRow && headerRow.nextElementSibling) {
            mastheadCol.insertBefore(panel, headerRow.nextElementSibling);
        } else {
            mastheadCol.appendChild(panel);
        }

        const panelId = `nsc-site-search-panel-${Math.random().toString(36).slice(2, 9)}`;
        panel.id = panelId;
        toggle.setAttribute("aria-controls", panelId);

        const desktopMq = window.matchMedia("(min-width: 64em)");

        function syncLayout() {
            if (desktopMq.matches) {
                closeMobileSearch(mount, panel, toggle, form);
                if (form.parentElement !== mount) {
                    mount.appendChild(form);
                }
            }
        }

        toggle.addEventListener("click", () => {
            if (desktopMq.matches) {
                form.querySelector('input[name="q"], input[type="search"]')?.focus();
                return;
            }
            const willOpen = !mount.classList.contains("is-open");
            if (willOpen) {
                mount.classList.add("is-open");
                toggle.setAttribute("aria-expanded", "true");
                panel.hidden = false;
                panel.appendChild(form);
                form.querySelector('input[name="q"], input[type="search"]')?.focus();
            } else {
                closeMobileSearch(mount, panel, toggle, form);
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && mount.classList.contains("is-open")) {
                closeMobileSearch(mount, panel, toggle, form);
                toggle.focus();
            }
        });

        if (typeof desktopMq.addEventListener === "function") {
            desktopMq.addEventListener("change", syncLayout);
        } else if (typeof desktopMq.addListener === "function") {
            desktopMq.addListener(syncLayout);
        }
        window.addEventListener("resize", syncLayout, { passive: true });
        syncLayout();
    }

    document.querySelectorAll("[data-nsc-site-search]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            const input = form.querySelector('input[name="q"], input[type="search"]');
            const query = (input && input.value ? input.value : "").trim();
            if (!query) {
                input?.focus();
                return;
            }
            window.location.href = searchPageUrl(query);
        });
        setupHeaderSearch(form);
    });

    const resultsRoot = document.getElementById("nsc-search-results");
    if (!resultsRoot) {
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const query = (params.get("q") || "").trim();
    const pageInput = document.getElementById("nsc-search-page-input");
    const summary = document.getElementById("nsc-search-summary");
    const list = document.getElementById("nsc-search-list");
    const empty = document.getElementById("nsc-search-empty");

    if (pageInput) {
        pageInput.value = query;
    }

    if (!query) {
        if (summary) {
            summary.textContent = "Enter a keyword to search pages, subjects, and staff.";
        }
        return;
    }

    if (summary) {
        summary.textContent = "Searching…";
    }

    fetch(`${assetBase()}data/site-search-index.json`, { cache: "no-cache" })
        .then((response) => {
            if (!response.ok) {
                throw new Error("Search index unavailable");
            }
            return response.json();
        })
        .then((entries) => {
            const terms = normalize(query).split(/\s+/).filter(Boolean);
            const ranked = entries
                .map((entry) => ({ entry, score: scoreEntry(entry, terms) }))
                .filter((item) => item.score > 0)
                .sort((a, b) => b.score - a.score || a.entry.label.localeCompare(b.entry.label))
                .slice(0, 40);

            if (summary) {
                summary.textContent =
                    ranked.length === 1
                        ? `1 result for “${query}”`
                        : `${ranked.length} results for “${query}”`;
            }

            if (!list) {
                return;
            }

            list.innerHTML = "";
            if (!ranked.length) {
                empty?.removeAttribute("hidden");
                return;
            }

            empty?.setAttribute("hidden", "hidden");
            for (const { entry } of ranked) {
                const item = document.createElement("li");
                item.className = "nsc-search-result";
                item.innerHTML = `
<a class="nsc-search-result__link" href="${entry.url}">
<span class="nsc-search-result__eyebrow">${entry.section || "Page"}</span>
<span class="nsc-search-result__title">${entry.label}</span>
<span class="nsc-search-result__desc">${entry.description || entry.title}</span>
</a>`;
                list.appendChild(item);
            }
        })
        .catch(() => {
            if (summary) {
                summary.textContent = "Sorry, search is temporarily unavailable.";
            }
        });
})();
