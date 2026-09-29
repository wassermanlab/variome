
import _ from 'lodash';

import Constants from './Constants';

var urlObj = new URL(import.meta.env.API_PATH, import.meta.env.BACKEND_ROOT);
const API_URL_BASE = urlObj.toString();
//const API_URL_BASE = import.meta.env.BACKEND_URL;//'http://127.0.0.1:8000/api/';

var map = {};

/*
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = _.trim(cookies[i]);
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}*/

var csrftoken;

var localStorageCachePrefix = "v1-";

function cachedFetch(
  url,
  query,
  method = 'GET',
  data,
  includeCredentials = true,
  localStorageKey
) {

  // NOTE: in settings.py CSRF_COOKIE_HTTPONLY = True blocks getting csrftoken from the cookie
  // we only need it for POST requests

  if (query){
    var params = new URLSearchParams(query);
    if (params.toString()) {
      url += '?' + params.toString();
    }
  }

  if (localStorageKey) {
    localStorageKey = localStorageCachePrefix + localStorageKey;

    try {
      const cached = localStorage.getItem(localStorageKey);
      if (cached) {
        return Promise.resolve(JSON.parse(cached));
      }
    } catch (e) {
      console.error("cache read", e);
    }
  }

  var key = url;

  if (!map[key]) {
    var options = {
      credentials: includeCredentials ? 'include' : 'omit',
      method,
      headers:{},
      body: data ? JSON.stringify(data) : null,
    };

    if (_.isString(csrftoken) && includeCredentials) {
      _.merge(options, {headers: {'X-Csrftoken':csrftoken}})
    }
    if (data){
      _.merge(options, {headers: {'Content-Type':'application/json'}})
    }

    map[key] = fetch(url, options)
      .then(response => {

        map[key] = null;

        if (response && response.status >= 200 && response.status < 300) {
          return response.json();
        } else if (response){
          throw response;
        } else {
          throw new Error(`No response from the server: ${url}`, options);
        }
      })
      .then((json) => {
        if (!_.isObject(json) && !_.isArray(json)) {
          return Promise.reject({ error: "The server's response was invalid", json });
        }

        if (_.isString(_.get(json, 'user.csrf_token'))) {
          csrftoken = json.user.csrf_token;
        }

        if (localStorageKey) {
          try {
            localStorage.setItem(localStorageKey, JSON.stringify(json));
          } catch (e) {
            console.error("cache write", e);
          }
        }

        map[key] = null;

        return json;
      })

  }

  return map[key];
}

function getFetch(url, query=null, localStorageKey){  
    return cachedFetch(url, query, 'GET', null, false, localStorageKey)
}

const Api = {
  get: async (path, query) => {
    var json;
    try {
      json = await cachedFetch(API_URL_BASE + path, query);
    } catch (response) {
      console.error("api error catch response:",response);
      return Promise.reject(response);
    }
    return json;
  },
  gnomadGraphQLRequest: async (query, variables) => {
    var json;
      try {
        json = await cachedFetch("https://gnomad.broadinstitute.org/api",
          null,
          'POST',
          {
            // collapse insignificant whitespace to cut request size
            query: _.isString(query) ? _.words(query, /\S+/g).join(' ') : query,
            variables
          },
          false
        );
      } catch (response) {
          console.error("gnomad.broadinstitute.org graph ql request failed", response);
        return Promise.reject(response);
      }
      return json;
    },
    ensemblRefCheck: async ({chr, pos, ref}, assemblyVersion) => {
      var json;
      var coordSystemVersion = Constants.assemblyVersions[assemblyVersion];

      var posEnd = _.toInteger(pos) + _.size(ref) - 1 ;
      
      if (_.isString(coordSystemVersion) && !_.isEmpty(coordSystemVersion)){
        
          json = await getFetch(
            `https://rest.ensembl.org/sequence/region/human/${chr}:${pos}..${posEnd}:1`,
            {"content-type":"application/json",
              "coord_system_version":coordSystemVersion
            },
            `ensemble:${chr}:${pos}..${posEnd}-${coordSystemVersion}`,
        ).catch ((e)=> {
          console.error("ensembl.org request failed", e);
          if (e && e.text && _.isFunction(e.text)){
            return e.text().then(t => {
              return Promise.reject(new Error(t));
            }
          );
          } else {
            return Promise.reject(e)
          }
        });

        /* uncomment to fake response delay 
        return new Promise((resolve, reject) => {
          setTimeout(() => {
            resolve(json);
          },10000)
        })*/

        return json;
      } else {
        return Promise.reject({ error: `Unsupported assembly version: ${assemblyVersion}. use "1" or "2". (2 is GRCh38)` });
      }
      
    }/*,
  post: async (path, data, query) => {
    try {
      return cachedFetch(import.meta.env.BACKEND_ROOT + path, query, 'POST', data);
    } catch ({ error, status, response }) {
      // ... i don't think this gets run (catches are in the fetch call above)
      console.error('Error fetching ' + path, error);
      return { errors: ["something went wrong"] };
    }
  }*/
}


export default Api