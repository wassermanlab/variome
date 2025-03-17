
import _ from "lodash";
import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { SearchContext } from './SearchProvider';
import { Box, List, ListItem, ListItemText } from "@mui/material"

export default function SearchResults({ sx }) {

  const navigate = useNavigate();

  const searchContext = useContext(SearchContext);



  return (
    <div sx={sx}>
      <h1>Search Results</h1>

      <Box style={{ position: "relative", top: "10px", left: "10px", width: "700px", height: "auto", overflow: "scroll" }}>
        {searchContext.summary}<br />
        loading? {searchContext.loading ? "true" : "false"}<br />
        {searchContext.resultsMessage}
        <pre>{JSON.stringify(searchContext.results, null, 2)}</pre>
        <List>
          {_.map(searchContext.results, (result, index) => {
            return <ListItem key={index} button onClick={(e) => onOptionClick(e, result)}>
              <ListItemText primary={`${result.variant_id} - ${result.var_type} - GRCh38`} />
            </ListItem>
          }
          )}
        </List>
      </Box>
    </div>
  )
}