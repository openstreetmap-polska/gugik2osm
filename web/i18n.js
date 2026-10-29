i18next
.use(i18nextHttpBackend)
.init({
    lng: 'pl', // default language
    fallbackLng: 'pl',
    debug: true,
    backend: {
        loadPath: `./locales${window.location.pathname === '/index.html' ? '/' : window.location.pathname.replace(/\.html$/, '/')}{{lng}}.json`
    }
}, function(err, t) {
    updateContent();
});

function updateContent() {
    document.querySelectorAll('[i18n]').forEach(el => {
        const key = el.getAttribute('i18n');
        el.innerHTML = i18next.t(key);
    });
    document.querySelectorAll('[i18n-title]').forEach(el => {
        const key = el.getAttribute('i18n-title');
        el['title'] = i18next.t(key);
    });
}

function updateLanguage(lang) {
    i18next.changeLanguage(lang, (err, t) => {
        if (err) return console.error(err);
        document.documentElement.lang = lang;
        document.querySelector('html').setAttribute('lang', lang);
        updateContent();
    });
}