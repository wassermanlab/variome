
import _ from "lodash";
import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { SearchContext } from './SearchProvider';
import { Box, List, ListItem, ListItemText } from "@mui/material"

import {Oval} from 'react-loader-spinner';

export default function SearchResults({ sx }) {

  const navigate = useNavigate();

  const searchContext = useContext(SearchContext);

  function openVariant(variant) {
    navigate(`/variant/${variant.id}`);
  }



  return (
    <div sx={sx}>

      <Box style={{ position: "relative", top: "10px", left: "10px", width: "700px", height: "auto", overflow: "scroll" }}>
        {searchContext.loading ? <Oval color="black" secondaryColor="grey" /> : <>
        
        {searchContext.summary}<br />
        <List>
          {_.map(searchContext.results, (result, index) => {
            return <ListItem key={index} button onClick={()=>openVariant(result)}>
              <ListItemText primary={`${result.variant_id} - ${result.var_type} - GRCh38`} />
            </ListItem>
          }
        )}
        </List>
        {searchContext.resultsMessage}
        <List>
          {_.map(searchContext.nearby, (result, index) => {
            return <ListItem key={index} button onClick={()=>openVariant(result)}>
              <ListItemText primary={`${result.variant_id} - ${result.var_type} - GRCh38`} onClick={()=>openVariant(result)}/>
            </ListItem>
          }
        )}
        </List>
        {/*}
        <pre>results...{JSON.stringify(searchContext.results, null, 2)}</pre>
        <pre>nearby...{JSON.stringify(searchContext.nearby, null, 2)}</pre> {*/}
        </>}<br />
      </Box>
    </div>
  )
}