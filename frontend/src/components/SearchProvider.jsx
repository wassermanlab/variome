import _ from "lodash";
import { createContext, useState, useRef, useEffect } from "react";

import Api from '../Api';

let variant_groups_regex = new RegExp(
  /^(CHR *)?(?<chr>[0-9]{1,2}|[XYM]{1}|MT)\s*[-:>\.\/ _]\s*(?<pos>(\d{1,3}([,. ]\d{3})+|(\d{1,})))\s*[-:>\.\/ _]?\s*(?<ref>[cgtaCGTA]{1,})?\s*[-:>\.\/ _]?\s*(?<alt>[cgtaCGTA]{1,})?$/,
  "i"
);

const DEBOUNCE_DELAY = 800;

export const SearchContext = createContext();

const parseParameters = (query) => {
  var match = query.match(variant_groups_regex);
  var groups = _.defaults(_.get(match, "groups"), {
    //    chr: null,
    //    pos: null,
    //    ref: null,
    //    alt: null
  });
  if (_.includes(groups.chr, "m") || _.includes(groups.chr, "M")) {
    //might be "MT"
    groups.chr = "M";
  }

  var resultsSetTests = {
    position: (term) => {
      return (
        !_.includes(term, "rs") &&
        _.isString(groups.chr) &&
        _.isString(groups.pos) &&
        !_.isEmpty(groups.chr) &&
        !_.isEmpty(groups.pos)
      );
    },
    dbsnp: (term) => {
      return _.includes(term, "rs") && _.size(term) > 5; // min lengh of valid dnsnp id ??
    },
    clinvar: (term) => {
      return _.isFinite(term * 1) && _.size(term) > 3; // min lengh of valid clinvar ??
    }
  };
  var resultSets = _.filter(_.keys(resultsSetTests), (setName) => {
    return resultsSetTests[setName](query);
  });
  console.log("r", resultSets);

  if (_.size(resultSets) > 0) {
    var searchSummaryGroups = groups;
    _.each(resultSets, (setName) => {
      if (setName != "position") {
        _.set(searchSummaryGroups, setName, query);
      }
    });

    return {
      searchParameters: {
        query,
        resultSets: resultSets.join(","),
        selectedAssembly: "GRCh38",
        chr: groups.chr,
        pos: groups.pos,
        ...groups.ref ? { ref: groups.ref } : {},//ref: groups.ref,
        ...groups.alt ? { alt: groups.alt } : {},//
      },
      groups: searchSummaryGroups
    };
  } else {
    console.log("not searchable:", query);
    return null;
  }
};


// a react component that doesn't have UI (render) but still uses state and effects
function SearchProvider({ children }) {
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [resultsMessage, setResultsMessage] = useState("");
  const [results, setResults] = useState([]);
  const [nearby, setNearby] = useState([]);
  const [summary, setSummary] = useState("results doo go here");

  const cancelledQueriesRef = useRef([]);
  const searchTimeoutRef = useRef(null);

  const debounceUpdateSearch = (newQuery) => {

    if (!_.isEmpty(newQuery)) {

      if (_.includes(cancelledQueriesRef.current, newQuery)) {
        //                console.log("uncancel", newQuery);
        cancelledQueriesRef.current = [..._.without(cancelledQueriesRef.current, newQuery)];
      }
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
        cancelledQueriesRef.current = [...cancelledQueriesRef.current, query]; // query is the previous query
      }

      setQuery(newQuery);
      setResults([]);
      setLoading(true);
      console.log("new query", newQuery);
      searchTimeoutRef.current = setTimeout(async () => {

        if (_.includes(cancelledQueriesRef.current, newQuery)) {
          //                    console.log("cancelledQueries", cancelledQueriesRef.current);
          //                    console.log("abort", newQuery);
        } else {

          var { results, nearby } = await doSearch(_.trim(newQuery));

          if (_.includes(cancelledQueriesRef.current, newQuery)) {
            console.log("(2) abort", newQuery);
          } else {
            console.log("setting results", results);
            console.log("set nearby", nearby);
            setResults(() => results);
            setNearby(() => nearby);

            cancelledQueriesRef.current = [];
            setLoading(() => false);
          }
        }

      }, DEBOUNCE_DELAY);


    } else {
      setResults([]);
      setNearby([]);
      setResultsMessage("? gone");
      setQuery("");
      cancelledQueriesRef.current = [];
      setLoading(() => false);
      //            console.log("set empty");
      //            console.log("cancelledQueries", cancelledQueriesRef.current);
    }
  }

  let doSearch = async function (query) {
    var nearby = [];
    var results = [];

    console.log("searching", query);
    //    setSummary("searching...");
    var parameters = parseParameters(query);
    console.log("parameters", parameters);

    //        groups = _.
    if (_.isEmpty(parameters) || !_.get(parameters, "searchParameters") || !_.get(parameters, "groups")) {

      //                        setResults(()=>[]);
      setLoading(() => false);
      setSummary("");
      setResultsMessage("No results ( query format is not recognized )");
    } else {
      try {

        var cleanGroups = _.omitBy(_.get(parameters, "groups", []), _.isNil);

        var pairs = _.map(_.toPairs(cleanGroups), ([key, val]) => {
          if (key == "dbsnp") {
            return [key, val];
          } else {
            return [key, _.toUpper(val)];
          }
        });

        setSummary(
          <div style={{ display: "flex", gap: "12px" }}>
            <label>Your search</label>
            {pairs.map(([key, val]) => {
              return (
                <span key={key}>
                  <span style={{ fontWeight: "bold" }}>
                    {" "}
                    {key}
                    {": "}
                  </span>
                  <span style={{}}>{val}</span>
                </span>
              );
            })}
          </div>
        );



        const variantData = await Api.get("search", parameters.searchParameters);

        results = _.compact(
          _.flatten([
            _.get(variantData, "results.dbsnp", []),
            _.get(variantData, "results.clinvar", []),
            _.get(variantData, "results.position", []),
            //      _.map(_.get(variantData, "results.nearby", []), (r) => {
            //        return { resultType: "nearby", ...r };
            //      })
          ])
        );
        //                console.log("debug", apex.debug.getLevel());
        //  var resultsWithLinks = _.map(resultsFlat, addLinkForResult);

        nearby = _.get(variantData, "results.nearby", [])
      } catch (error) {
        console.error(error);
        setLoading(() => false);
        //        if (searchResult.errors && _.size(searchResult.errors) > 0) {
        setResultsMessage(`Sorry, something went wrong`);
        //      }
      }

      if (_.size(results) == 0 && _.size(nearby) == 1) {
        setResultsMessage(`No variants found at location. 1 variant nearby:`);
      } else if (_.size(results) == 0 && _.size(nearby) > 1) {
        setResultsMessage(
          `No variants found at location. ${_.size(nearby)} variants nearby:`
        );
      } else if (_.size(results) == 0 && _.size(nearby) == 0) {
        setResultsMessage(`No variants found.`);
      } else if (_.size(nearby) > 1) {
        setResultsMessage(`${_.size(nearby)} variants nearby:`);
      } else if (_.size(nearby) == 1) {
        setResultsMessage(`1 variant nearby:`);
      } else {
        setResultsMessage("");
      }
    }
    return { results, nearby };
  };

  return (
    <SearchContext.Provider
      value={{
        debounceUpdateSearch,
        summary,
        loading,
        results,
        nearby,
        resultsMessage
      }}
    >
      {children}
    </SearchContext.Provider>
  );
}




export default SearchProvider;
