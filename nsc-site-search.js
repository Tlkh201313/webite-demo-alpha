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
