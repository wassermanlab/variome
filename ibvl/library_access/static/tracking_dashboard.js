/*
import _ from "lodash";
import { useState } from "react";
*/
const useState = React.useState;


function TrackingDashboard() {
  const [data, setData] = useState("hello");

  return <div>Tracking Dashboard (react {data})</div>;
}
