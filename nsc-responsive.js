/**
 * Device / viewport utilities for NSC static pages.
 * Sets --nsc-vw/--nsc-vh on <html> and wraps scrollable tables.
 * Note: Core responsiveness is handled via native CSS media queries.
 */
(function () {
    if (window.__nscResponsiveInit) {
        return;
    }
    window.__nscResponsiveInit = true;

    const root = document.documentElement;

    function updateViewportVars() {
        root.style.setProperty("--nsc-vw", window.innerWidth * 0.01 + "px");
        root.style.setProperty("--nsc-vh", window.innerHeight * 0.01 + "px");
    }

    function updateChromeOffset() {
        const chrome = document.getElementById("site-chrome");
        if (!chrome) {
            return;
        }
        const h = Math.ceil(chrome.getBoundingClientRect().height);
        if (h > 0) {
            root.style.setProperty("--nsc-chrome-h", h + "px");
            root.style.scrollPaddingTop = h + "px";
        }
    }

    function wrapEntryTables() {
        // Wrap tables if on smaller screens (less than 1024px)
        if (window.innerWidth >= 1024) {
            return;
        }
        document.querySelectorAll(".entry-content table").forEach((table) => {
            if (table.closest(".nsc-table-wrap")) {
                return;
            }
            const wrap = document.createElement("div");
            wrap.className = "nsc-table-wrap";
            wrap.setAttribute("role", "region");
            wrap.setAttribute("aria-label", "Scrollable table");
            wrap.setAttribute("tabindex", "0");
            table.parentNode.insertBefore(wrap, table);
            wrap.appendChild(table);
        });
    }

    function tameHeroMotion() {
        if (window.innerWidth >= 768) {
            return;
        }
        document.querySelectorAll("#hero-parallax").forEach(function (el) {
            el.style.transform = "none";
        });
    }

    function revealHeroCopy() {
        if (window.innerWidth >= 768) {
            return;
        }
        document
            .querySelectorAll("section.relative.flex.items-center.overflow-hidden .max-w-2xl, section.relative.flex.items-center.overflow-hidden .max-w-3xl")
            .forEach(function (block) {
                block.querySelectorAll("h1, p, span, a, div").forEach(function (el) {
                    el.classList.remove("opacity-0");
                    el.style.setProperty("opacity", "1", "important");
                    el.style.setProperty("color", "#ffffff", "important");
                    el.style.setProperty("-webkit-text-fill-color", "#ffffff", "important");
                    el.style.setProperty("animation", "none", "important");
                    el.style.setProperty("transform", "none", "important");
                });
            });
    }

    function apply() {
        updateViewportVars();
        updateChromeOffset();
        tameHeroMotion();
        revealHeroCopy();
        wrapEntryTables();
    }

    let resizeTimer = 0;
    window.addEventListener(
        "resize",
        function () {
            window.clearTimeout(resizeTimer);
            resizeTimer = window.setTimeout(function () {
                updateViewportVars();
                updateChromeOffset();
                tameHeroMotion();
                revealHeroCopy();
            }, 100);
        },
        { passive: true }
    );
    window.addEventListener("orientationchange", apply);

    function observeChrome() {
        const chrome = document.getElementById("site-chrome");
        if (!chrome || typeof ResizeObserver === "undefined") {
            return;
        }
        const ro = new ResizeObserver(function () {
            updateChromeOffset();
        });
        ro.observe(chrome);
    }

    function onReady() {
        apply();
        observeChrome();
        window.setTimeout(updateChromeOffset, 250);
        window.setTimeout(updateChromeOffset, 1000);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", onReady);
    } else {
        onReady();
    }

    window.addEventListener("load", updateChromeOffset, { passive: true });
})();
