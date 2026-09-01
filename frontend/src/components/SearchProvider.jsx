import _ from "lodash";
import { createContext, useState } from "react";

import Constants from '../Constants';

const ASSEMBLY_LABEL = Constants.assemblyVersions["2"];

import Api from '../Api';

let variant_groups_regex = new RegExp(
  /^(CHR *)?(?<chr>[0-9]{1,2}|[XYM]{1}|MT)\s*[-:>\.\/ _]\s*(?<pos>(\d{1,3}([,. ]\d{3})+|(\d{1,})))\s*[-:>\.\/ _]?\s*(?<ref>[cgtaCGTA]{1,})?\s*[-:>\.\/ _]?\s*(?<alt>[cgtaCGTA]{1,})?$/,
  "i"
);

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

  if (_.size(resultSets) > 0) {
    var searchSummaryGroups = groups;
    _.each(resultSets, (setName) => {
      if (setName != "position") {
        _.set(searchSummaryGroups, setName, query);
      }
    });


    if (_.get(import.meta.env, "DEV")) {
      const params = new URLSearchParams(window.location.search);
      var response_code_param = params.get('r');
    }


    return {
      searchParameters: {
        query,
        resultSets: resultSets.join(","),
        selectedAssembly: "GRCh38",
        chr: groups.chr,
        pos: groups.pos,
        ...groups.ref ? { ref: groups.ref } : {},//ref: groups.ref,
        ...groups.alt ? { alt: groups.alt } : {},//
        ... response_code_param ? { r: response_code_param } : {}
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
  const [resultsMessage, setResultsMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [results, setResults] = useState([]);
  const [nearby, setNearby] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [matchPairs, setMatchPairs] = useState([]);
  const [hideResultsOverride, setHideResultsOverride] = useState(false);

  const submitSearch = async (newQuery) => {
    const trimmedQuery = _.trim(newQuery);
    setHideResultsOverride(false);

    if (!_.isEmpty(trimmedQuery)) {
      setQuery(trimmedQuery);
      setResults([]);
      setNearby([]);
      setLoading(true);
      setWarnings([]);
      setErrorMessage(null);

      const { results, nearby } = await doSearch(trimmedQuery);
      setResults(results);
      setNearby(nearby);
      setLoading(false);
    } else {
      setWarnings([]);
      setResults([]);
      setNearby([]);
      setResultsMessage(null);
      setErrorMessage(null);
      setQuery("");
      setLoading(false);
    }
  }

  let doSearch = async function (query) {
    var nearby = [];
    var results = [];
    var error = null;

    var parameters = parseParameters(query);

    if (_.isEmpty(parameters) || !_.get(parameters, "searchParameters") || !_.get(parameters, "groups")) {

      setLoading(() => false);
      setMatchPairs([]);
      setResultsMessage("No results ( query format is not recognized )");
    } else {

      var cleanGroups = _.omitBy(_.get(parameters, "groups", []), _.isNil);

      var pairs = _.map(_.toPairs(cleanGroups), ([key, val]) => {
        if (key == "dbsnp") {
          return [key, val];
        } else {
          return [key, _.toUpper(val)];
        }
      });

      setMatchPairs(() => pairs);
      setWarnings(() => []); 
      if (parameters.searchParameters.ref) {
        const referenceCheck = Promise.race([
          Api.ensemblRefCheck(parameters.searchParameters, "2"),
          new Promise(resolve => setTimeout(() => resolve(null), 5000))
        ]);

        const referenceResult = await referenceCheck;

        if (_.isObject(referenceResult) && _.get(referenceResult, "seq")) {
          if (referenceResult.seq == _.get(parameters, "groups.ref", "").toUpperCase()) {
            console.log("check passes");
          } else {
            console.log("reference mismatch", referenceResult.seq, _.get(parameters, "groups.ref", "").toUpperCase());
            console.log(referenceResult);
            setWarnings(warnings => [
              ...warnings,
              {
                label: `⚠️ The ${ASSEMBLY_LABEL} Reference is ${referenceResult.seq} at this position`
              }
            ]);
            console.log("warnings", warnings);
          }
        }
      }

      try {
        const variantData = await Api.get("search", parameters.searchParameters).catch((e) => {
        
        if (_.get(e, "status") == 403) {
          error = "You have been logged out. Please refresh the page, and log in again.";
        } else {
          error = _.get(e, "error", "Unknown error");
        }
        throw e;
      });

        results = _.compact(
          _.flatten([
            _.get(variantData, "results.dbsnp", []),
            _.get(variantData, "results.clinvar", []),
            _.get(variantData, "results.position", []),
          ])
        );

        nearby = _.get(variantData, "results.nearby", [])

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
          setResultsMessage(null);
        }
      } catch {
        
              if (error) {
                setResultsMessage('An error occured during search.');
                setErrorMessage(error);
              }

      }
    }
    return { results, nearby };
  };

  function onInputFocus() {
    setHideResultsOverride(false);
  }

  return (
    <SearchContext.Provider
      value={{
        submitSearch,
        matchPairs,
        loading,
        results,
        nearby,
        query,
        setQuery,
        onInputFocus,
        hideResultsOverride,
        setHideResultsOverride,
        warnings,
        resultsMessage,
        errorMessage
      }}
    >
      {children}
    </SearchContext.Provider> 
  );
}

export default SearchProvider;
