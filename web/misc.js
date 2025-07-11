function processesInfo () {
    fetch('/processes.json')
        .then((response) => {
          return response.json();
        })
        .then((data) => {
            console.log(data);
            var temp = '<table>';
            data.processes.forEach((el) => {
                temp += `<tr><td><b>Nazwa:</b></td><td><b>${el.name}</b></td>`;
                if (el.in_progress) {
                    temp += `<tr><td>Czy w trakcie:</td><td style="background-color: #66ff33;">Tak</td>`;
                } else {
                    temp += `<tr><td>Czy w trakcie:</td><td>Nie</td>`;
                }
                temp += `<tr><td>Czas rozpoczęcia:</td><td>${el.start_time}</td>`;
                if (el.end_time != null) {
                    temp += `<tr><td>Czas zakończenia:</td><td>${el.end_time}</td>`;
                }
                if (el.no_of_tiles_to_process != null && el.no_of_tiles_to_process >= 0) {
                    temp += `<tr><td>Kafle pozostałe do przetworzenia:</td><td>${el.no_of_tiles_to_process}</td>`;
                }
                if (el.last_status != null) {
                    temp += `<tr><td>Status ostatniego wykonania:</td><td>${el.last_status}</td>`;
                }
            });
            temp += '</table>';
            $('#procinfo').html(temp);
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
}

function updateLanguage(lang) {
    i18next.changeLanguage(lang, (err, t) => {
        if (err) return console.error(err);
        updateContent();
    });
}