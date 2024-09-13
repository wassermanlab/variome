/*
import _ from "lodash";
import { useState } from "react";
*/
const useState = React.useState;


function TrackingDashboard({initialdata}) {
  const [data, setData] = useState(initialdata);
  

  return <div>Tracking Dashboard (react)
    <pre>{JSON.stringify(data, null, 2)}</pre>
    
  </div>;
}


function VariantViews(){
  {/*}
    <div class="views-table panel">
            <h5>Variant Views</h5>
            <div>
              <div></div>
              <ul style={{display:"flex", flexDirection:"column"}}>
                {% for pageview in variant_pageviews %}
                  <li class="row">
                    <div>
                      <a href="{{ pageview.variant_url }}_asdf" target="_blank">{{ pageview.variant }}</a>
                    </div>
                    <div>{{ pageview.view_time }}</div>
                    <div>{{ pageview.visitor.user.get_full_name }}</div>
                  </li>
                {% endfor %}
              </ul>
            </div>
          </div>

          {*/}
          return <div>Variant Views go here</div>;
}


function UserDetails(){

  {/*}
    <div class="panel">
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
                {% for stat in data.user_stats %}
                  <tr>stat
                    <td>{{ stat.user.get_full_name }}</td>
                    <td>{{ stat.page_views_unique }}</td>
                    <td>{{ stat.24_hrs }}</td>
                    <td>{{ stat.time_on_site }}</td>
                  </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>

          {*/}

          return <div>User Details go here</div>;
}


function VariantDetails(){
  {/*}
    <div class="panel">
            <h5>Variant Details</h5>
            <table>
              <thead>
                <tr>
                  <th>Variant</th>
                  <th>Users</th>
                </tr>
              </thead>
              <tbody>
                {% for detail in variant_access_details|dictsort:"user_count"|slice:":-1" %}
                  <tr>
                    <td>{{ detail.name }}</td>
                    <td>
                      <ul>
                        <li>
                          {{ detail.user_count }} Users:
                            <span style={{ cursor: "pointer" }} title="Hover for more info">ⓘ
                            <ul>
                              {detail.users.map(user => (
                              <li key={user.id}>{user.get_full_name} ({user.email})</li>
                              ))}
                            </ul>
                            </span>
                        </li>
                      </ul>
                    </td>
                  </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          {*/}
          return <div>Variant Details go here</div>;
}