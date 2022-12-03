const ctx = document.getElementById('forecast');

console.log(PeriodEnd)
moment.tz.setDefault("Europe/Berlin")


new Chart(ctx, {
    type: 'line',
    data: {
      labels: PeriodEnd,
      datasets: [
        { 
          data: PVEst10,
          label: "PVEst10",
          borderColor: "red",
          backgroundColor: "red",
          fill: true,
          tension: 0.6,
          opacity: 33
        },{ 
          data: PVEst,
          label: "PVEst",
          borderColor: "#fcd14d",
          backgroundColor: "#fcd14d",
          fill: true,
          tension: 0.6,
          opacity: 33
        },{ 
          data: PVEst90,
          label: "PVEst90",
          borderColor: "green",
          backgroundColor: "green",
          fill: true,
          tension: 0.6,
          opacity: 33
        }
      ]
    },
    options: {
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      },
      title: {
        display: true,
        text: 'Solar-Energy Forecast'
      },
      scales: {
        x: {
            type: 'time',
            time: {
                unit: 'day',
                parser: function (timestamp) {
                  const m = moment.tz(timestamp,"Europe/Berlin");
                  return m;
                }
            },
            grid: {

                borderColor: '#989490',
                color: '#989490'
            }
        },
        y: {
          suggestedMax: 12,
          suggestedMin: 0,
          position: 'left',
          
      },
      }
    }
  });
  