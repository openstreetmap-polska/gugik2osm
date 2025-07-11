function processesInfo () {
    fetch('/processes.json')
        .then((response) => {
          return response.json();
        })
        .then((data) => {
            console.log(data);
            var temp = '<table>';
            data.processes.forEach((el) => {
                temp += `<tr><td><b i18n="processes.name"></b></td><td><b>${el.name}</b></td>`;
                if (el.in_progress) {
                    temp += `<tr><td i18n="processes.in-progress"></td><td style="background-color: #66ff33;" i18n="processes.yes"></td>`;
                } else {
                    temp += `<tr><td i18n="processes.in-progress"></td><td i18n="processes.yes"></td>`;
                }
                temp += `<tr><td i18n="processes.start-time"></td><td>${el.start_time}</td>`;
                if (el.end_time != null) {
                    temp += `<tr><td i18n="processes.end-time"></td><td>${el.end_time}</td>`;
                }
                if (el.no_of_tiles_to_process != null && el.no_of_tiles_to_process >= 0) {
                    temp += `<tr><td i18n="processes.no-of-tiles-to-process"></td><td>${el.no_of_tiles_to_process}</td>`;
                }
                if (el.last_status != null) {
                    temp += `<tr><td i18n="processes.last-status"></td><td>${el.last_status}</td>`;
                }
            });
            temp += '</table>';
            $('#procinfo').html(temp);
            updateContent();
    });
}

i18next
.use(i18nextHttpBackend)
.init({
    lng: 'pl', // default language
    fallbackLng: 'pl',
    debug: true,
    backend: {
        loadPath: './locales/{{lng}}.json'
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