/**
 * NSC first-load skeleton — hide when page + assets ready (min display, max timeout).
 * Applies layout hints from the real page DOM (sidebar, home hero).
 */
(function () {
    if (window.__nscSkeletonInit) {
        return;
    }
    window.__nscSkeletonInit = true;

    const loader = document.getElementById('nsc-skeleton-loader');
    if (!loader) {
        return;
    }

    const MIN_MS = 200;
    const MAX_MS = 3000;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const started = performance.now();
    let done = false;

    const path = (window.location.pathname || '').toLowerCase();
    const isHome =
        /(^|\/)main\.html?$/.test(path) ||
        path.endsWith('/') ||
        path === '' ||
        /index\.html?$/.test(path) && !document.querySelector('.nsc-inner-banner');
    const hasInnerBanner = !!document.querySelector('.nsc-inner-banner');
    const hasSidebar = !!document.querySelector('.nsc-page-with-sidebar');

    if (hasSidebar) {
        loader.classList.add('nsc-skeleton--sidebar');
    }
    if (isHome && !hasInnerBanner) {
        loader.classList.add('nsc-skeleton--home');
    }

    document.documentElement.classList.add('nsc-skeleton-active');

    function teardown() {
        document.documentElement.classList.remove('nsc-skeleton-active');
        document.body.style.removeProperty('overflow');
        document.documentElement.style.removeProperty('overflow');
        loader.remove();
    }

    function hide(force) {
        if (done) {
            return;
        }
        done = true;
        loader.setAttribute('aria-hidden', 'true');
        loader.removeAttribute('aria-busy');
        loader.classList.add('nsc-skeleton--hidden');

        if (reducedMotion.matches || force) {
            window.setTimeout(teardown, reducedMotion.matches ? 140 : 420);
            return;
        }

        const onEnd = (event) => {
            if (event.target !== loader) {
                return;
            }
            teardown();
        };
        loader.addEventListener('transitionend', onEnd);
        window.setTimeout(teardown, 460);
    }

    function hideAfterMin() {
        const elapsed = performance.now() - started;
        const wait = Math.max(0, MIN_MS - elapsed);
        window.setTimeout(() => hide(false), wait);
    }

    if (document.readyState === 'complete') {
        hideAfterMin();
    } else {
        window.addEventListener('load', hideAfterMin, { once: true });
    }

    window.setTimeout(() => hide(true), MAX_MS);
})();
