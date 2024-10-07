/*
import _ from "lodash";
import { useState } from "react";
*/
const useState = React.useState;


function TrackingDashboard({ initialdata }) {
  const [data, setData] = useState(initialdata);


  return <>


    <VariantViews views={data.variant_pageviews} />
    <div id="dashboard-page-body">

      <ViewsChart views={data.variant_pageviews}/>
        <UserDetails users={data.user_details} />
        <VariantDetails variants={data.variant_access_details} />
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>

  </>;
}


function VariantViews({ views }) {

  // truncating the variant names 
  function truncateText(text, maxLength) {
    if (text.length > maxLength) {
      return text.substring(0, maxLength) + "...";
  }
    return text;
  }

  return <div className="views-table">
      <ul style={{ display: "flex", flexDirection: "column" }}>

        {views.map((pageview, i) => (
          <li className="row" key={i}>
            <div>
              {truncateText(pageview.variant, 20)} 
            </div>
              <div>{(() => {
                const timeString = pageview.time.includes("Z") ? pageview.time : pageview.time + "Z";
                const dateObject = new Date(timeString);
                return dateObject.toLocaleString();
              })()}</div>
            <div style={{textAlign: "right"}}>{pageview.user}</div>
          </li>
        ))}

        {views.length === 0 && <li style={{textAlign: "center"}}>(No tracked views under selected filters)</li>}
      </ul>
  </div>
}


function ViewsChart({ views }) {
  
  const ChartRef = React.useRef(null);

  // chart state Strictly only these three values (daily, weekly, monthly)
  const [chartTimeView, updateChartTimeView] = useState('monthly'); 

  // need to keep track of chart instance every time switching timelines
  const [chartInstance, setChartInstance] = useState(null);

  React.useEffect(() => {
    let chartData = {'daily': {}, 'weekly': {}, 'monthly': {}};
    
    // convert to browser timezone
    const variant_pageviews = views.map((view) => {
      const timeString = view.time.includes("Z") ? view.time : view.time + "Z";
      const dateObject = new Date(timeString);

      return {...view, time: dateObject};
    });

    // count the data for the charts 
    // daily
    variant_pageviews.forEach((item) => {
      const date = new Date(item.time).toLocaleDateString();

      if (chartData['daily'][date]) {
        chartData['daily'][date]++;
      } else {
        chartData['daily'][date] = 1;
      }
    })

    // helper function for weekly 
    function startOfTheWeek(date) {
      const day = date.getDay(); 
      const diff = date.getDate() - day; 
      return new Date(date.setDate(diff)).toLocaleDateString();
    }

    // weekly
    variant_pageviews.forEach((item) => {
      const date = new Date(item.time).toLocaleDateString();

      // finding start of the week
      const weekStartDate = startOfTheWeek(new Date(date));

      if (chartData['weekly'][weekStartDate]) {
        chartData['weekly'][weekStartDate]++;
      } else {
        chartData['weekly'][weekStartDate] = 1;
      }
    })

    // monthly 
    variant_pageviews.forEach((item) => {
      const date = new Date(item.time);

      const yearMonth = date.getFullYear() + "-" + (date.getMonth() + 1).toString();

      if (chartData['monthly'][yearMonth]) {
        chartData['monthly'][yearMonth]++;
      } else {
        chartData['monthly'][yearMonth] = 1;
      }

    })


    // destroys an already made chart instant
    if (chartInstance) {
      chartInstance.destroy();
    }

    var lineGraphCtx = ChartRef.current
      .getContext("2d");


    const currentChartTable = chartData[chartTimeView];

    const data = {
      labels: Object.keys(currentChartTable),
      datasets: [{
        label: `${chartTimeView}`,
        data: Object.values(currentChartTable),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    };

    const chart = new Chart(lineGraphCtx, {
      type: "line",
      data,
      options: {
        responsive: true,
        scales: {
          y: {
            ticks: {
              beginAtZero: true,
              stepSize: 1,
            },
            min: 0,
          }
        }
      }
    });

    setChartInstance(chart);

  }, [ChartRef, chartTimeView, views])


  return <div style={{ height: "75vh", width: "100%", position: "relative", marginBottom:"2em" }}>
    <button className="btn waves-effect waves-light btn-small" onClick={(e) => {
      e.preventDefault();
      updateChartTimeView('daily');
    }}>Daily</button>
    <button style={{marginLeft: "1px", marginRight: "1px"}} className="btn waves-effect waves-light btn-small" onClick={(e) => {
      e.preventDefault();
      updateChartTimeView('weekly');
    }}>Weekly</button>
    <button className="btn waves-effect waves-light btn-small" onClick={(e) => {
      e.preventDefault();
      updateChartTimeView('monthly');
    }}>Monthly</button>
    <canvas id="lineGraphChart" ref={ChartRef} ></canvas>
  </div>;
}


function UserDetails({ users }) {

  return <div style={{ width: "50%"}}>
    <h5>User Details</h5>
    <table>
      <thead>
        <tr>
          <th>User</th>
          <th># Unique Views</th>
          <th># Views in 24h</th>
          <th>Avg. Time on Site</th>
        </tr>
      </thead>
      <tbody>
        {users.map((user, i) => {
          return <tr key={i}>
            <td>{user.name}</td>
            <td>{user.page_views_unique}</td>
            <td>{user.views_24_hrs}</td>
            <td>{user.time_on_site}</td>
          </tr>
        })
        }
      </tbody>
    </table>
  </div>

}


function VariantDetails({ variants }) {

  return <div style={{ width: "50%" }}>
    <h5>Variant Details</h5>
    <table>
      <thead>
        <tr>
          <th>Variant</th>
          <th>Users</th>
        </tr>
      </thead>
      <tbody>
        {
          variants.map((variant, i) => {
            return <tr key={i}>
              <td>{variant.name}</td>
              <td>
                <ul>
                  <li>{variant.user_count} Users:</li>
                  <span style={{ cursor: "pointer" }} title="Hover for more info">ⓘ</span>
                  {variant.users.map((user, j) => {
                    return <li key={j}>{user.get_full_name} ({user.email})</li>
                  })}
                </ul>
              </td>
            </tr>
          })
        }
      </tbody>
    </table>
  </div>

}