function processesInfo () {
    fetch('https://budynki.openstreetmap.org.pl/processes/')
        .then((response) => {
          return response.json();
        })
        .then((data) => {
            console.log(data);
            var temp = '<table>';
            data.processes.forEach((el) => {
                temp += `<tr><td><b>Nazwa:</b></td><td><b>${el.name}</b></td>`;
                temp += `<tr><td>Czy w trakcie:</td><td>${el.in_progress}</td>`;
                temp += `<tr><td>Czas rozpoczęcia:</td><td>${el.start_time}</td>`;
                temp += `<tr><td>Czas zakończenia:</td><td>${el.end_time}</td><tr><td></td><td></td></tr>`;
            });
            temp += '</table>';
            $('#procinfo').html(temp);
        }
    });
}
