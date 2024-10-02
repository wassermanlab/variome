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

      <ViewsChart chartData={data.chart_data}/>
        <UserDetails users={data.user_details} />
        <VariantDetails variants={data.variant_access_details} />
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>

  </>;
}


function VariantViews({ views }) {

  return <div className="views-table">
      <ul style={{ display: "flex", flexDirection: "column" }}>

        {views.map((pageview, i) => (
          <li className="row" key={i}>
            <div>
              {pageview.variant}
            </div>
              <div>{pageview.time.includes('T') ? pageview.time.split('T')[0] : pageview.time}</div>
            <div>{pageview.user}</div>
          </li>
        ))}

        {views.length === 0 && <li style={{textAlign: "center"}}>(No tracked views under selected filters)</li>}
      </ul>
  </div>
}


function ViewsChart({ chartData }) {

  const ChartRef = React.useRef(null);

  // chart state Strictly only these three values (daily, weekly, monthly)
  const [chartTimeView, updateChartTimeView] = useState('monthly'); 

  // need to keep track of chart instance every time switching timelines
  const [chartInstance, setChartInstance] = useState(null);

  React.useEffect(() => {

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



  }, [ChartRef, chartTimeView])


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