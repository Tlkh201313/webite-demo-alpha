/**
 * Secure login dropdown — toggle, dismiss, keyboard.
 */
(function () {
    if (window.__nscSecureLoginInit) {
        return;
    }
    window.__nscSecureLoginInit = true;

    const roots = document.querySelectorAll('[data-nsc-secure-login]');
    if (!roots.length) {
        return;
    }

    const siteChrome = document.getElementById('site-chrome');
    const mobileMq = window.matchMedia('(max-width: 47.99em)');
    let openRoot = null;
    let backdrop = null;

    function ensureBackdrop() {
        if (backdrop) {
            return backdrop;
        }
        backdrop = document.createElement('div');
        backdrop.className = 'nsc-secure-login__backdrop';
        backdrop.hidden = true;
        backdrop.setAttribute('aria-hidden', 'true');
        backdrop.addEventListener('click', closeAll);
        document.body.appendChild(backdrop);
        return backdrop;
    }

    function setBackdropVisible(visible) {
        if (!mobileMq.matches) {
            if (backdrop) {
                backdrop.hidden = true;
            }
            return;
        }
        const layer = ensureBackdrop();
        layer.hidden = !visible;
    }

    function closeAll() {
        roots.forEach((root) => {
            const trigger = root.querySelector('.nsc-secure-login__trigger');
            const panel = root.querySelector('.nsc-secure-login__panel');
            if (!trigger || !panel) {
                return;
            }
            root.classList.remove('is-open');
            trigger.setAttribute('aria-expanded', 'false');
            panel.hidden = true;
        });
        siteChrome?.classList.remove('nsc-secure-login-open');
        setBackdropVisible(false);
        document.body.classList.remove('nsc-secure-login-body-lock');
        openRoot = null;
    }

    function open(root) {
        const trigger = root.querySelector('.nsc-secure-login__trigger');
        const panel = root.querySelector('.nsc-secure-login__panel');
        if (!trigger || !panel) {
            return;
        }
        if (openRoot && openRoot !== root) {
            closeAll();
        }
        root.classList.add('is-open');
        trigger.setAttribute('aria-expanded', 'true');
        panel.hidden = false;
        siteChrome?.classList.add('nsc-secure-login-open');
        setBackdropVisible(true);
        if (mobileMq.matches) {
            document.body.classList.add('nsc-secure-login-body-lock');
        }
        openRoot = root;
    }

    roots.forEach((root) => {
        const trigger = root.querySelector('.nsc-secure-login__trigger');
        const panel = root.querySelector('.nsc-secure-login__panel');
        if (!trigger || !panel) {
            return;
        }

        trigger.addEventListener('click', (event) => {
            event.stopPropagation();
            const isOpen = root.classList.contains('is-open');
            if (isOpen) {
                closeAll();
            } else {
                open(root);
            }
        });

        panel.querySelectorAll('a[href]').forEach((link) => {
            link.addEventListener('click', () => {
                closeAll();
            });
        });
    });

    mobileMq.addEventListener('change', () => {
        if (!openRoot) {
            return;
        }
        if (!mobileMq.matches) {
            setBackdropVisible(false);
            document.body.classList.remove('nsc-secure-login-body-lock');
        } else {
            setBackdropVisible(true);
            document.body.classList.add('nsc-secure-login-body-lock');
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeAll();
        }
    });

    document.addEventListener('click', (event) => {
        if (!openRoot) {
            return;
        }
        if (openRoot.contains(event.target)) {
            return;
        }
        if (backdrop && event.target === backdrop) {
            return;
        }
        closeAll();
    });
})();
