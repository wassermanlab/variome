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

      <ViewsChart views={data.variant_pageviews} />
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
            <div>{pageview.time}</div>
            <div>{pageview.user}</div>
          </li>
        ))}

        {views.length === 0 && <li>(No tracked views under selected filters)</li>}
      </ul>
  </div>
}


function ViewsChart({ views }) {

  const ChartRef = React.useRef(null);


  React.useEffect(() => {

    var lineGraphCtx = ChartRef.current
      .getContext("2d");

    const data = {
      labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
      datasets: [{
        label: 'My First Dataset',
        data: [65, 59, 80, 81, 56, 55, 40],
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    };

    new Chart(lineGraphCtx, {
      type: "line",
      data,
      options: {
        responsive: true,
      }
    });
  }, [ChartRef])


  return <div style={{ height: "75vh", width: "100%", position: "relative", marginBottom:"2em" }}>
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