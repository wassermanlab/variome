/*
import _ from "lodash";
import { useState } from "react";
*/
const useState = React.useState;

// for truncating text when names get too big
function truncateText(text, maxLength) {
  if (text.length > maxLength) {
    return text.substring(0, maxLength) + "...";
}
  return text;
}

function TrackingDashboard({ initialdata }) {
  const [data, setData] = useState(initialdata);


  return <>


    <VariantViews views={data.variant_pageviews} />
    <div id="dashboard-page-body">

      <ViewsChart views={data.variant_pageviews} filters={data.filter_details}/>
        <UserDetails users={data.user_details} />
        <VariantDetails variants={data.variant_access_details} />
      <pre>{ /*JSON.stringify(data, null, 2) */}</pre>
    </div>

  </>;
}


function VariantViews({ views }) {

  return <div className="views-table">
      <ul style={{ display: "flex", flexDirection: "column", margin: "0px"}}>
        {views.map((pageview, i) => (
          <li className="row" key={i}>
            <div className="variant-column">
              {truncateText(pageview.variant, 20)} 
            </div>
              <div className="time-column">{(() => {
                const timeString = pageview.time.includes("Z") ? pageview.time : pageview.time + "Z"; // converting UTC to browser timezone
                const dateObject = new Date(timeString);
                return dateObject.toLocaleString();
              })()}</div>
            <div className="user-column" style={{textAlign: "right"}}>{pageview.user}</div>
          </li>
        ))}

        {views.length === 0 && <li style={{textAlign: "center", margin: "1em"}}>(No tracked views under selected filters)</li>}
      </ul>
  </div>
}


function ViewsChart({ views , filters }) {
  
  const ChartRef = React.useRef(null);

  // chart state Strictly only these three values (daily, weekly, monthly)
  const [chartTimeView, updateChartTimeView] = useState('daily'); 

  // need to keep track of chart instance every time switching timelines
  const [chartInstance, setChartInstance] = useState(null);

  React.useEffect(() => {
    let chartData = {'daily': {}, 'weekly': {}, 'monthly': {}};
    
    if (filters.valid_form) {
    // convert to browser timezone
    const variant_pageviews = views.map((view) => {
      const timeString = view.time.includes("Z") ? view.time : view.time + "Z";
      const dateObject = new Date(timeString);

      return {...view, time: dateObject};
    });

    // for weekly view
    function startOfTheWeek(date) {
      const newDate = new Date(date);
      const day = newDate.getDay();
      const diff = newDate.getDate() - day + (day === 0 ? -6 : 1); // start of the week is monday
      return new Date(newDate.setDate(diff)).toLocaleDateString();
    }


    function createDateBuckets(startDate, endDate, bucketType) {
      const buckets = {};
      let currentDate = new Date(startDate);
      
      while (currentDate <= endDate) {
        let bucketKey;
        
        if (bucketType === 'daily') {
          bucketKey = currentDate.toLocaleDateString();
        } else if (bucketType === 'weekly') {
          bucketKey = startOfTheWeek(currentDate);
        } else if (bucketType === 'monthly') {
          bucketKey = `${currentDate.getMonth() + 1}/${currentDate.getFullYear()}`;
        }
        
        if (!buckets[bucketKey]) {
          buckets[bucketKey] = 0;
        }
        
        if (bucketType === 'daily') {
          currentDate.setDate(currentDate.getDate() + 1);
        } else if (bucketType === 'weekly') {
          currentDate.setDate(currentDate.getDate() + 7);
        } else if (bucketType === 'monthly') {
          currentDate.setDate(1);
          currentDate.setMonth(currentDate.getMonth() + 1);
        }
      }
      
      return buckets;
    }

    // formats to local timezone date
    let startDateUTC = filters.start_time.includes("Z") ? filters.start_time : filters.start_time + "Z";
    let endDateUTC = filters.end_time.includes("Z") ? filters.end_time : filters.end_time + "Z";
    const startDate = new Date(startDateUTC);
    const endDate = new Date(endDateUTC);

    chartData['daily'] = createDateBuckets(startDate, endDate, 'daily');
    chartData['weekly'] = createDateBuckets(startDate, endDate, 'weekly');
    chartData['monthly'] = createDateBuckets(startDate, endDate, 'monthly');

    variant_pageviews.forEach((item) => {
      // Daily
      const dailyKey = item.time.toLocaleDateString();
      if (chartData['daily'][dailyKey] !== undefined) {
        chartData['daily'][dailyKey]++;
      }
    
      // Weekly
      const weeklyKey = startOfTheWeek(item.time);
      if (chartData['weekly'][weeklyKey] !== undefined) {
        chartData['weekly'][weeklyKey]++;
      }
    
      // Monthly
      const monthlyKey = `${item.time.getMonth() + 1}/${item.time.getFullYear()}`;
      if (chartData['monthly'][monthlyKey] !== undefined) {
        chartData['monthly'][monthlyKey]++;
      }
    });

    function sortChartData(data) {
      return Object.keys(data).sort((a, b) => new Date(a) - new Date(b))
        .reduce((sorted, key) => {
          sorted[key] = data[key];
          return sorted;
        }, {});
    }

    chartData['daily'] = sortChartData(chartData['daily']);
    chartData['weekly'] = sortChartData(chartData['weekly']);
    chartData['monthly'] = sortChartData(chartData['monthly']);

  }
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
  return <div className="users-table" style={{ marginRight: "1em"}}>
    <h5>User Details</h5>
    <table>
      <thead>
        <tr>
          <th style={{ borderLeft: 'none' }}>User</th>
          <th># Unique Views</th>
          <th># Views in 24h</th>
          <th style={{ borderRight: 'none' }}>Avg. Time on Site</th>
        </tr>
      </thead>
      <tbody>
        {users.map((user, i) => {
          return <tr key={i}>
            <td style={{ borderLeft: 'none' }}>{user.name}</td>
            <td>{user.page_views_unique}</td>
            <td>{user.views_24_hrs}</td>
            <td style={{ borderRight: 'none' }}>{user.time_on_site}</td>
          </tr>
        })
        }
      </tbody>
    </table>
  </div>

}


function VariantDetails({ variants }) {

  const [hoveredTracker, setHoveredTracker] = useState(null);

  return <div className="variant-table">
    <h5>Variant Details</h5>
    <table>
      <thead>
        <tr>
          <th style={{ borderLeft: 'none' }}>Variant</th>
          <th style={{ borderRight: 'none' }}>Users</th>
        </tr>
      </thead>
      <tbody>
        { 
          variants.map((variant, i) => {
            return <tr key={i}>
                <td style={{ borderLeft: 'none' }}>{truncateText(variant.name, 20)}</td>
                <td style={{ borderRight: 'none' }}>
                <ul>
                  <li>{variant.user_count} Users:</li>
                  {variant.users.map((user, j) => {
                    return <li key={j}>
                      {user.get_full_name} 
                      <span style={{ cursor: "pointer" }}
                        onMouseEnter={() => setHoveredTracker(j.toString() + ":" + i.toString())}
                        onMouseLeave={() => setHoveredTracker(null)}> ⓘ</span>
                        {hoveredTracker === (j.toString() + ":" + i.toString()) &&
                        <div style={{
                          position: "absolute",
                          backgroundColor: '#f9f9f9',
                          border: '1px solid #ddd',
                          boxShadow: '0px 4px 8px rgba(0, 0, 0, 0.1)',
                          zIndex: '1',
                          whiteSpace: 'nowrap',
                        }}>
                          <p style={{ padding: "0", margin: "0.2em 0"}}>Username: {user.username}</p>
                          <p style={{ padding: "0", margin: "0.2em 0"}}>Email: {user.email}</p>
                        </div>
                        }
                      </li>
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