/*
import _ from "lodash";
import { useState } from "react";
*/
const useState = React.useState;


function TrackingDashboard({ initialdata }) {
  const [data, setData] = useState(initialdata);


  return <div>Tracking Dashboard (react)

    <VariantViews views={data.variant_pageviews} />
    <div className="below-filters-and-views-table">

      <ViewsChart views={data.variant_pageviews} />
      <div className="flex">
        <UserDetails users={data.user_details}/>
        <VariantDetails variants={data.variant_access_details}/>
      </div>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>

  </div>;
}


function VariantViews({ views }) {

  return <div className="views-table panel">
    <h5>Variant Views</h5>
    <div>
      <div></div>
      <ul style={{ display: "flex", flexDirection: "column" }}>

        {views.map((pageview, i) => (
          <li className="row" key={i}>
            <div>
              <a href={pageview.variant_url} target="_blank">{pageview.variant}</a>
            </div>
            <div>{pageview.time}</div>
            <div>{pageview.user}</div>
          </li>
        ))}
      </ul>
    </div>
  </div>
}


function ViewsChart({ views }) {
  
  const ChartRef = React.useRef(null);
  
  
  React.useEffect(() => {

    var lineGraphCtx = ChartRef.current
    .getContext("2d");

    console.log("got 2d context", lineGraphCtx);
    
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
  }, [ChartRef, window.innerWidth])


  return <div style={{border:"solid 1px black", height:"400px", width: "100%", position:"relative"}}>
    <canvas id="lineGraphChart" ref={ChartRef} ></canvas>
  </div>;
}


function UserDetails({ users }) {

    return    <div style={{width:"50%", border: "1px solid cyan", margin:"-1px"}}>
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
                {users.map( (user, i) => {
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


function VariantDetails( { variants }) {
  
  return <div style={{width:"50%", border: "1px solid green", margin:"-1px"}}>
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
                  variants.map( (variant, i) => {
                    return <tr key={i}>
                      <td>{variant.name}</td>
                      <td>
                        <ul>
                          <li>{variant.user_count} Users:</li>
                          <span style={{ cursor: "pointer" }} title="Hover for more info">ⓘ</span>
                          {variant.users.map( (user, j) => {
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