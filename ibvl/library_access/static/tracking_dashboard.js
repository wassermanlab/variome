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
