/**
 * Device / viewport detection for NSC static pages.
 * Sets data-device, data-orientation, and --nsc-vw/--nsc-vh on <html>.
 */
(function () {
    if (window.__nscResponsiveInit) {
        return;
    }
    window.__nscResponsiveInit = true;

    const root = document.documentElement;
    const mobileMq = window.matchMedia("(max-width: 47.99em)");
    const tabletMq = window.matchMedia("(min-width: 48em) and (max-width: 63.99em)");
    const portraitMq = window.matchMedia("(orientation: portrait)");
    const coarseMq = window.matchMedia("(pointer: coarse)");

    function deviceCategory() {
        if (mobileMq.matches) {
            return "mobile";
        }
        if (tabletMq.matches) {
            return "tablet";
        }
        return "desktop";
    }

    function updateViewportVars() {
        root.style.setProperty("--nsc-vw", window.innerWidth * 0.01 + "px");
        root.style.setProperty("--nsc-vh", window.innerHeight * 0.01 + "px");
    }

    function wrapEntryTables() {
        const device = deviceCategory();
        if (device === "desktop") {
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
        const device = deviceCategory();
        root.dataset.device = device;
        root.dataset.orientation = portraitMq.matches ? "portrait" : "landscape";
        root.dataset.touch = coarseMq.matches ? "true" : "false";
        updateViewportVars();
        wrapEntryTables();
    }

    function onMqChange() {
        apply();
    }

    [mobileMq, tabletMq, portraitMq, coarseMq].forEach((mq) => {
        if (typeof mq.addEventListener === "function") {
            mq.addEventListener("change", onMqChange);
        } else if (typeof mq.addListener === "function") {
            mq.addListener(onMqChange);
        }
    });

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
