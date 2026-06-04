/**
 * NSC scroll entrance animations — single init for all static pages.
 */
(function () {
    if (window.__nscRevealInit) {
        return;
    }
    window.__nscRevealInit = true;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const REVEAL_SELECTOR =
        '.reveal-on-scroll, .reveal-from-left, .reveal-from-right, .reveal-scale, .value-card, .learning-split-reveal';
    const STAGGER_SELECTOR =
        '.reveal-stagger-group, .learning-stagger, .british-values-grid, .rs-values-grid';
    const ALL_SELECTOR = REVEAL_SELECTOR + ', ' + STAGGER_SELECTOR;
    const STAGGER_CHILD_SELECTOR = '.reveal-stagger-child, .british-value-pill, .rs-value-pill';

    const OBSERVER_OPTIONS = {
        root: null,
        rootMargin: '0px 0px -3% 0px',
        threshold: [0, 0.03, 0.06, 0.1],
    };

    function applyVisible(el) {
        el.classList.add('is-visible');
        if (reducedMotion.matches) {
            el.style.opacity = '1';
            el.style.transform = 'none';
            el.style.transition = 'none';
        }
    }

    function revealAll() {
        document.querySelectorAll(ALL_SELECTOR).forEach(applyVisible);
        document.querySelectorAll(STAGGER_CHILD_SELECTOR).forEach((child) => {
            if (reducedMotion.matches) {
                child.style.opacity = '1';
                child.style.transform = 'none';
                child.style.transition = 'none';
            }
        });
    }

    function flushInView() {
        const vh = window.innerHeight || document.documentElement.clientHeight;
        const margin = Math.min(120, vh * 0.08);

        document.querySelectorAll(ALL_SELECTOR).forEach((el) => {
            if (el.classList.contains('is-visible')) {
                return;
            }
            const rect = el.getBoundingClientRect();
            if (rect.bottom > -margin && rect.top < vh + margin) {
                applyVisible(el);
            }
        });

        document.querySelectorAll('.entry-content img[loading="lazy"]').forEach((img) => {
            const rect = img.getBoundingClientRect();
            if (rect.bottom > 0 && rect.top < vh && !img.complete) {
                img.loading = 'eager';
            }
        });
    }

    function bindScrollFlush() {
        let ticking = false;
        const onScroll = () => {
            if (ticking) {
                return;
            }
            ticking = true;
            requestAnimationFrame(() => {
                ticking = false;
                flushInView();
            });
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        window.addEventListener('resize', onScroll, { passive: true });
    }

    function initRevealObservers() {
        if (reducedMotion.matches) {
            revealAll();
            return;
        }

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }
                applyVisible(entry.target);
                obs.unobserve(entry.target);
            });
        }, OBSERVER_OPTIONS);

        document.querySelectorAll(ALL_SELECTOR).forEach((el) => observer.observe(el));

        flushInView();
        requestAnimationFrame(flushInView);
        bindScrollFlush();

        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                revealAll();
            }
        });

        window.setTimeout(flushInView, 180);
    }

    function whenSkeletonReady(run) {
        if (!document.documentElement.classList.contains('nsc-skeleton-active')) {
            run();
            return;
        }

        const done = () => {
            observer.disconnect();
            window.clearTimeout(fallback);
            requestAnimationFrame(run);
        };

        const observer = new MutationObserver(() => {
            if (!document.documentElement.classList.contains('nsc-skeleton-active')) {
                done();
            }
        });
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class'],
        });
        const fallback = window.setTimeout(done, 3200);
    }

    function boot() {
        whenSkeletonReady(initRevealObservers);
    }

    reducedMotion.addEventListener('change', () => {
        if (reducedMotion.matches) {
            revealAll();
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
