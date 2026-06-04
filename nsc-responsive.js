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

    function apply() {
        updateViewportVars();
        wrapEntryTables();
    }

    let resizeTimer = 0;
    window.addEventListener(
        "resize",
        function () {
            window.clearTimeout(resizeTimer);
            resizeTimer = window.setTimeout(function () {
                updateViewportVars();
            }, 100);
        },
        { passive: true }
    );
    window.addEventListener("orientationchange", apply);

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", apply);
    } else {
        apply();
    }
})();
