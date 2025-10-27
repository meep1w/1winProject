// ./static/js/i18n.js
(function (w) {
    const DEFAULT_LANG = 'ru';
    const STORE_KEY = 'rtp_lang_v1';

    const I18N = {
        lang: DEFAULT_LANG,
        dict: {},
        ready: Promise.resolve(),

        init({ lang, localesPath = './static/locales.json' } = {}) {
            // язык: query -> storage -> tg -> default
            const params = new URLSearchParams(location.search);
            const tgLang = w.Telegram?.WebApp?.initDataUnsafe?.user?.language_code;
            const chosen =
                (lang || params.get('lang') || localStorage.getItem(STORE_KEY) || tgLang || DEFAULT_LANG)
                    .toLowerCase();

            this.lang = chosen;
            try { localStorage.setItem(STORE_KEY, this.lang); } catch {}

            this.ready = fetch(localesPath, { cache: 'no-store' })
                .then(r => r.json())
                .then(json => { this.dict = json; })
                .catch(() => { this.dict = {}; });

            return this.ready;
        },

        t(path, fallback = '') {
            const pack = this.dict[this.lang] || this.dict[DEFAULT_LANG] || {};
            const val = path.split('.').reduce((acc, k) => (acc && acc[k] != null ? acc[k] : undefined), pack);
            return (val != null ? val : fallback);
        },

        // авто-проставление: data-i18n, data-i18n-html, data-i18n-attr="placeholder|title"
        apply(root = document) {
            root.querySelectorAll('[data-i18n]').forEach(el => {
                el.textContent = this.t(el.getAttribute('data-i18n')) || '';
            });
            root.querySelectorAll('[data-i18n-html]').forEach(el => {
                el.innerHTML = this.t(el.getAttribute('data-i18n-html')) || '';
            });
            root.querySelectorAll('[data-i18n-attr]').forEach(el => {
                const attr = el.getAttribute('data-i18n-attr'); // placeholder|title|aria-label
                const key  = el.getAttribute('data-i18n-key');
                if (attr && key) el.setAttribute(attr, this.t(key) || '');
            });
        },

        setLang(code) {
            this.lang = (code || DEFAULT_LANG).toLowerCase();
            try { localStorage.setItem(STORE_KEY, this.lang); } catch {}
            this.apply(document);
        }
    };

    w.I18N = I18N;
})(window);
